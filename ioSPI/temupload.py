import requests
from pathlib import Path


class TEMUpload:
    def __init__(self, token):
        self.headers = {"Authorization": f"Bearer {token}"}
        self.base_url = "https://api.osf.io/v2/"

        requests.get(self.base_url, headers=self.headers).raise_for_status()

        self.dataset_node_guid = "24htr"

    def upload_dataset_from_tem(self, tem_sim):
        existing_molecules = self.get_existing_molecules()
        molecule_label = tem_sim.path_dict["pdb_keyword"]
        dataset_label = (
            tem_sim.path_dict["pdb_keyword"] + t.path_dict["micrograph_keyword"]
        )

        if molecule_label not in existing_molecules.keys():
            molecule_guid = self.post_child_node(self.dataset_node_guid, molecule_label)
        else:
            molecule_guid = existing_molecules[molecule_label]

        dataset_guid = self.post_child_node(
            molecule_guid, dataset_label, tags=self.get_dataset_tags(tem_sim)
        )

        upload_file_paths = [tem_sim.output_path_dict["h5_file"]]
        self.post_files(dataset_guid, upload_file_paths)

    def post_child_node(self, parent_guid, title, tags=None):

        request_url = f"{self.base_url}nodes/{parent_guid}/children"

        request_body = {
            "type": "nodes",
            "attributes": {"title": title, "category": "data", "public": True},
        }

        if tags is not None:
            request_body["attributes"]["tags"] = tags

        response = requests.post(
            request_url, headers=self.headers, data={"data": request_body}
        )
        response.raise_for_status()

        return response["data"]["id"]

    def get_existing_molecules(self):
        request_url = f"{self.base_url}nodes/{self.dataset_node_guid}/children"
        response = requests.get(request_url, headers=self.headers)
        response.raise_for_status()
        dataset_node_children = response.json()["data"]

        existing_molecules = {
            child["attributes"]["title"]: child["id"] for child in dataset_node_children
        }

        return existing_molecules

    def generate_tags_from_tem(self, tem_wrapper):
        pass

    def post_files(self, dataset_guid, file_paths):

        files_base_url = "https://files.osf.io/v1/resources/"
        request_url = f"{files_base_url}{dataset_guid}/providers/osfstorage"

        for file_path_string in file_paths:
            file_path = Path(file_path_string)
            files = {file_path.name: open(file_path, "rb")}
            query_parameters = f"?kind=file&name={file_path.stem}"

            response = requests.post(
                request_url + query_parameters, files=files, headers=self.headers
            )

            if response.status_code != 200:
                print(f"Upload {file_path} failed with code{response.status_code}")
