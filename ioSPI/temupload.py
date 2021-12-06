import requests




class TEMUpload:
    def __init__(self, token):
        self.headers = {'Authorization': f"Bearer {token}"}
        self.base_url = "https://api.osf.io/v2/";

        requests.get(self.base_url, headers = self.headers).raise_for_status()

        #  Project Page -> Data
        self.dataset_node_guid = '24htr'

    def upload_dataset(self, tem_sim):
        existing_molecules = self.get_existing_molecules()
        molecule_label, dataset_label = self.get_labels_from_tem()

        if (molecule_label not in existing_molecules.keys()):
            # create molecule node
            pass

        # create dataset node
        molecule_node_url = ''
        # upload files

            pass

    def get_existing_molecules(self):
        req_url = f"{self.base_url}nodes/{self.dataset_node_guid}/children"
        response = requests.get(req_url, headers = self.headers)
        response.raise_for_status()
        dataset_node_children = response.json()['data']

        existing_molecules = {child['attributes']['title']: child['id'] for child in dataset_node_children}

        return existing_molecules

    def get_labels_from_tem(self):
        pass

    def get_dataset_tags(self):
        pass

    def create_

    def post_node(self):
        pass

    def post_files(self):
        pass


if __name__ == "__main__":

    t = TEMUpload(token)
    a = t.get_existing_molecules()
    print(a)
