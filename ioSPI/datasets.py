"""Module to house methods related to datasets (micrographs, meta-data, etc.)."""

import os


class OSFProject:
    """Class to list, download and upload data from an OSF project using osfclient library.

    Parameters
    ----------
    username : str
        Username corresponding to an account on OSF.
        E.g. email address used to create an OSF account.
    token : str
        Personal token from osf.io.
        See: https://osf.io/settings/tokens
    project_id : str, default = "7g42j"
        Identifier of the project, found on the OSF project page.
        E.g. 7g42j for project at https://osf.io/7g42j/

    See Also
    --------
    osfclient: https://github.com/osfclient/osfclient
    OSF API documentation : https://developer.osf.io/
    """

    def __init__(self, username: str, token: str, project_id: str = "7g42j") -> None:
        self.username = username
        self.token = token
        self.project_id = project_id

        config_path = os.path.join(".osfcli.config")
        with open(config_path, "w") as out_file:
            out_file.write("[osf]\n")
            out_file.write(f"username = {username}\n")
            out_file.write(f"project = {project_id}\n")
            out_file.write(f"token = {token}\n")
        print("OSF config written to .osfcli.config!")

    def ls(self):
        """List all files in the project."""
        print(f"Listing files from OSF project: {self.project_id}...")
        os.system("osf ls")

    @staticmethod
    def download(remote_path, local_path):
        """Download file from osf and save it locally.

        Parameters
        ----------
        remote_path : str
            Remote path of the file on OSF.
            E.g. osfstorage/
            randomrot1D_nodisorder/
            4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        local_path : str
            Local path where the file will be saved.
            E.g. 4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        """
        print(f"Downloading {remote_path} to {local_path}...")
        os.system(f"osf fetch {remote_path} {local_path}")
        print("Done!")

    @staticmethod
    def upload(remote_path, local_path):
        """Upload file to osf.

        Notes
        -----
        You should have requested permission to upload to the project first.

        Parameters
        ----------
        remote_path : str
            Remote path of the file on OSF.
            E.g. osfstorage/
            randomrot1D_nodisorder/
            4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        local_path : str
            Local path where the file will be saved.
            E.g. 4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        """
        print(f"Uploading {local_path} to {remote_path}...")
        os.system(f"osf upload {local_path} {remote_path}")
        print("Done!")
