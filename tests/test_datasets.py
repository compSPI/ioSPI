"""Unit tests for listing/uploading/downloading datasets on an OSF project.

These assume the tests are executed in a Conda environment and GitHub actions
when tested non-locally.
"""

import os
import random
import string
import subprocess

import pytest

from ioSPI import datasets


@pytest.fixture(autouse=True, scope="session")
def setup():
    """Set up for tests."""
    print("Creating a test project for dataset")
    project = datasets.OSFProject(
        username="ninamio78@gmail.com",
        token="HBGGBOJcLYQfadEKIOyXJiLTum3ydXK4nGP3KmbkYUeBuYkZma9LPBSYennQn92gjP2NHn",
        project_id="xbr2m",
        osfclient_path="$CONDA/bin/",
    )
    yield project


@pytest.fixture(autouse=True, scope="session")
def set_file_path():
    """Set up a temporary text file path for upload.

    Set local_testing = True when testing locally, False if on GitHub.
    """
    file_path = "tests/data/"
    local_testing = False
    if not local_testing:
        file_path = "/home/runner/work/ioSPI/ioSPI/" + file_path

    file_name = (
        "test_upload-"
        + "".join(random.choice(string.ascii_letters) for i in range(5))
        + ".txt"
    )
    return file_path, file_name


@pytest.fixture(autouse=True, scope="session")
def create_test_file(set_file_path):
    """Create a temporary text file for upload."""
    with open(set_file_path[0] + set_file_path[1], "w") as f:
        f.write("Hello World!")


def test_constructor_valid():
    """Test the constructor."""
    project = datasets.OSFProject(
        username="ninamio78@gmail.com",
        token="HBGGBOJcLYQfadEKIOyXJiLTum3ydXK4nGP3KmbkYUeBuYkZma9LPBSYennQn92gjP2NHn",
    )
    assert project.username is not None
    assert project.token is not None
    assert project.project_id is not None
    assert project.storage is not None


def test_constructor_invalid_because_no_username():
    """Test if an error is raised when no username is provided to the constructor."""
    with pytest.raises(TypeError):
        datasets.OSFProject(token="token")


def test_constructor_invalid_because_no_token():
    """Test if an error is raised when no token is provided to the constructor."""
    with pytest.raises(TypeError):
        datasets.OSFProject(username="username")


def test_upload_valid(setup, set_file_path):
    """Test the upload method."""
    setup.upload(set_file_path[0] + set_file_path[1], set_file_path[1])
    file_exists = False
    file_list = setup.ls()
    for line in file_list:
        file_exists = set_file_path[1] == line.split("/")[1].strip()
        if file_exists:
            break

    assert file_exists
    subprocess.run(f"rm {set_file_path[0]}{set_file_path[1]}", shell=True, check=True)


def test_upload_invalid_because_no_local_path(setup):
    """Test if an error is raised when no local_path is provided."""
    with pytest.raises(TypeError):
        setup.upload(remote_path="remote_path")


def test_upload_invalid_because_no_remote_path(setup):
    """Test if an error is raised when no remote_path is provided."""
    with pytest.raises(TypeError):
        setup.upload(local_path="local_path")


def test_download_valid(setup, set_file_path):
    """Test the download method."""
    setup.download(set_file_path[1], set_file_path[0] + set_file_path[1])
    assert os.path.exists(set_file_path[0] + set_file_path[1])
    subprocess.run(f"rm {set_file_path[0]}{set_file_path[1]}", shell=True, check=True)


def test_download_invalid_because_no_remote_path(setup):
    """Test if an error is raised when no remote_path is provided."""
    with pytest.raises(TypeError):
        setup.download(local_path="local_path")


def test_download_invalid_because_no_local_path(setup):
    """Test if an error is raised when no local_path is provided."""
    with pytest.raises(TypeError):
        setup.download(remote_path="remote_path")


def test_remove_valid(setup, set_file_path):
    """Test the remove method."""
    setup.remove(set_file_path[1])
    file_exists = False
    file_list = setup.ls()
    for line in file_list:
        file_exists = set_file_path[1] == line.split("/")[1].strip()
        if file_exists:
            break

    assert not file_exists


def test_remove_invalid_because_no_remote_path(setup):
    """Test if an error is raised when no remote_path is provided."""
    with pytest.raises(TypeError):
        setup.remove()
