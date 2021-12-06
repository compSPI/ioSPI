import requests
from pathlib import Path


class TEMUpload:
    def __init__(self, token, data_component_guid="24htr"):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        self.base_url = "https://api.osf.io/v2/"

        requests.get(self.base_url, headers=self.headers).raise_for_status()

        self.dataset_node_guid = data_component_guid

    def upload_dataset_from_tem(self, tem_sim):

        dataset_label = (
            tem_sim.path_dict["pdb_keyword"] + t.path_dict["micrograph_keyword"]
        )
        molecule_label = tem_sim.path_dict["pdb_keyword"]
        molecule_guid = self.get_molecule_guid(molecule_label)
        dataset_guid = self.post_child_node(
            molecule_guid, dataset_label, tags=self.get_dataset_tags(tem_sim)
        )

        upload_file_paths = [tem_sim.output_path_dict["h5_file"]]
        return self.post_files(dataset_guid, upload_file_paths)

    def get_molecule_guid(self, molecule_label):
        existing_molecules = self.get_existing_molecules()
        if molecule_label not in existing_molecules.keys():
            return self.post_child_node(self.data_component_guid, molecule_label)
        else:
            return existing_molecules[molecule_label]

    def generate_tags_from_tem(self, tem_wrapper):
        pass

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

        return response.json()["data"][0]["id"]

    def get_existing_molecules(self):
        request_url = f"{self.base_url}nodes/{self.data_component_guid}/children"
        response = requests.get(request_url, headers=self.headers)
        response.raise_for_status()
        dataset_node_children = response.json()["data"]

        existing_molecules = {
            child["attributes"]["title"]: child["id"] for child in dataset_node_children
        }

        return existing_molecules

    def post_files(self, dataset_guid, file_paths):

        files_base_url = "http://files.ca-1.osf.io/v1/resources/"
        request_url = f"{files_base_url}{dataset_guid}/providers/osfstorage/"
        success = True

        for file_path_string in file_paths:
            file_path = Path(file_path_string)

            with open(file_path, "rb") as f:
                data = f.read()

            files = {file_path.name: open(file_path, "rb")}
            query_parameters = f"?kind=file&name={file_path.name}"
            print(request_url + query_parameters)
            response = requests.put(
                request_url + query_parameters, data=str(data), headers=self.headers
            )

            if response.status_code != 201:
                print(f"Upload {file_path} failed with code {response.status_code}")
                success = False
            else:
                print(f"Uploaded {file_path} ")

        return success
