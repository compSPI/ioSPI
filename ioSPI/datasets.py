"""Module to house methods related to datasets (micrographs, meta-data, etc.)."""

import os


class OSFProject:
    """Class to list, download and upload data in an OSF project using osfclient library.

    Parameters
    ----------
    username : str
        Username corresponding to an account on OSF.
        E.g. email address used to create an OSF account.
    token : str
        Personal token from osf.io.
        See: https://osf.io/settings/tokens
    project_id : str, default = "xbr2m"
        Identifier of the project, found on the OSF project page.
        E.g. xbr2m for project at https://osf.io/xbr2m/
    storage : str, default = "osfstorage"
        Storage provider of the project.

    See Also
    --------
    osfclient: https://github.com/osfclient/osfclient
    OSF API documentation : https://developer.osf.io/
    """

    def __init__(
        self,
        username: str,
        token: str,
        project_id: str = "xbr2m",
        storage: str = "osfstorage",
    ) -> None:
        if username is None:
            raise TypeError("username must be provided.")
        self.username = username

        if token is None:
            raise TypeError("token must be provided.")
        self.token = token

        self.project_id = project_id
        self.storage = storage

        config_path = os.path.join(".osfcli.config")
        with open(config_path, "w") as out_file:
            out_file.write("[osf]\n")
            out_file.write(f"username = {username}\n")
            out_file.write(f"project = {project_id}\n")
            out_file.write(f"token = {token}\n")
            # out_file.write(f"storage = {storage}\n")
        print("OSF config written to .osfcli.config!")

    def ls(self):
        """List all files in the project."""
        print(f"Listing files from OSF project: {self.project_id}...")
        os.system("osf ls")

    def download(self, remote_path: str, local_path: str):
        """Download a file from an OSF project and save it locally.

        Parameters
        ----------
        remote_path : str
            Remote path of the file in an OSF project,
            which will be appended to the project storage name (by default, osfstorage).
            E.g. osfstorage/
            randomrot1D_nodisorder/
            4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        local_path : str
            Local path where the file will be saved.
            E.g. 4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        """
        if remote_path is None:
            raise TypeError("remote_path must be provided.")
        if local_path is None:
            raise TypeError("local_path must be provided.")

        full_remote_path = self.storage + "/" + remote_path
        print(f"Downloading {full_remote_path} to {local_path}...")
        os.system(f"osf fetch {full_remote_path} {local_path}")
        print("Done!")

    def upload(self, local_path: str, remote_path: str):
        """Upload a file to an OSF project.

        Notes
        -----
        You should have requested permission to upload to the project first.

        Parameters
        ----------
        local_path : str
            Local path where the file will be saved.
            E.g. 4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        remote_path : str
            Remote path of the file in an OSF project,
            which will be appended to the project storage name (by default, osfstorage).
            E.g. osfstorage/
            randomrot1D_nodisorder/
            4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        """
        if local_path is None:
            raise TypeError("local_path must be provided.")
        if remote_path is None:
            raise TypeError("remote_path must be provided.")

        full_remote_path = self.storage + "/" + remote_path
        print(f"Uploading {local_path} to {full_remote_path}...")
        os.system(f"osf upload {local_path} {full_remote_path}")
        print("Done!")

    def remove(self, remote_path: str):
        """Remove a file in an OSF project.

        Parameters
        ----------
        remote_path : str
            Remote path of the file to remove in an OSF project,
            which will be appended to the project storage name (by default, osfstorage).
            E.g. osfstorage/
            randomrot1D_nodisorder/
            4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        """
        if remote_path is None:
            raise TypeError("remote_path must be provided.")

        full_remote_path = self.storage + "/" + remote_path
        print(f"Removing {full_remote_path} in the project...")
        os.system(f"osf remove {full_remote_path}")
        print("Done!")
