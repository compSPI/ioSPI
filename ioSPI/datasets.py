"""Module to house methods related to datasets (micrographs, meta-data, etc.)."""

import io
import os
import subprocess


class OSFProject:
    """Class to list, download and upload data in an OSF project.

    It uses osfclient library.

    Parameters
    ----------
    username : str, default = None
        Username corresponding to an account on OSF.
        E.g. email address used to create an OSF account.
    token : str, default = None
        Personal token from osf.io.
        See: https://osf.io/settings/tokens
    project_id : str, default = "xbr2m"
        Identifier of the project, found on the OSF project page.
        E.g. xbr2m for project at https://osf.io/xbr2m/
    storage : str, default = "osfstorage"
        Storage provider of the project.
    osfclient_path : str, default = None

    See Also
    --------
    osfclient: https://github.com/osfclient/osfclient
    OSF API documentation : https://developer.osf.io/
    """

    def __init__(
        self,
        username: str = None,
        token: str = None,
        project_id: str = "xbr2m",
        storage: str = "osfstorage",
        osfclient_path: str = None,
    ) -> None:
        if username is None:
            raise TypeError("username must be provided.")
        self.username = username

        if token is None:
            raise TypeError("token must be provided.")
        self.token = token

        self.project_id = project_id
        self.storage = storage
        self.osfclient_path = osfclient_path
        self.osfclient_command = "osf "
        if osfclient_path is not None:
            self.osfclient_command = self.osfclient_path + self.osfclient_command

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
        file_list = subprocess.run(
            self.osfclient_command + "ls",
            shell=True,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
        ).stdout

        return io.StringIO(file_list).readlines()

    def download(self, remote_path: str = None, local_path: str = None):
        """Download a file from an OSF project and save it locally.

        Parameters
        ----------
        remote_path : str, default = None
            Remote path of the file in an OSF project,
            which will be appended to the project storage name (by default, osfstorage).
            E.g. osfstorage/
            randomrot1D_nodisorder/
            4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        local_path : str, default = None
            Local path where the file will be saved.
            E.g. 4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        """
        if remote_path is None:
            raise TypeError("remote_path must be provided.")
        if local_path is None:
            raise TypeError("local_path must be provided.")

        full_remote_path = self.storage + "/" + remote_path
        print(f"Downloading {full_remote_path} to {local_path}...")
        subprocess.run(
            self.osfclient_command + f"fetch {full_remote_path} {local_path}",
            shell=True,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
        )
        print("Done!")

    def upload(self, local_path: str = None, remote_path: str = None):
        """Upload a file to an OSF project.

        Notes
        -----
        You should have requested permission to upload to the project first.

        Parameters
        ----------
        local_path : str, default = None
            Local path where the file will be saved.
            E.g. 4v6x_randomrot_copy6_defocus3.0_yes_noise.txt
        remote_path : str, default = None
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
        subprocess.run(
            self.osfclient_command + f"upload {local_path} " f"{full_remote_path}",
            shell=True,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
        )
        print("Done!")

    def remove(self, remote_path: str = None):
        """Remove a file in an OSF project.

        Parameters
        ----------
        remote_path : str, default = None
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
        subprocess.run(
            self.osfclient_command + f"remove {full_remote_path}",
            shell=True,
            text=True,
            check=True,
            stdout=subprocess.PIPE,
        )
        print("Done!")
