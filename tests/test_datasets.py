"""Unit tests for listing/uploading/downloading datasets on an OSF project.

These assume the tests are executed in a Conda environment.
"""

import io
import os
import subprocess

import pytest

from ioSPI import datasets


@pytest.fixture(autouse=True, scope="session")
def setup():
    """Test node creation and clean-up for tests."""
    print("Creating a test project for dataset")
    project = datasets.OSFProject(
        username="ninamio78@gmail.com",
        token="HBGGBOJcLYQfadEKIOyXJiLTum3ydXK4nGP3KmbkYUeBuYkZma9LPBSYennQn92gjP2NHn",
        project_id="xbr2m",
    )

    yield project


@pytest.fixture(autouse=True, scope="session")
def set_file_path():
    """Create a temporary text file for upload."""
    file_path = "/home/runner/work/ioSPI/ioSPI/tests/data/"
    file_name = "test_upload.txt"
    return file_path, file_name


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
    # file_list = os.popen("osf ls")
    file_list = subprocess.run(
        "$CONDA/bin/" + "osf ls",
        shell=True,
        text=True,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    file_list = io.StringIO(file_list)
    line = file_list.readline()
    while line:
        print(line)
        file_exists = set_file_path[1] == line.split("/")[1].strip()
        if file_exists:
            break
        line = file_list.readline()

    assert file_exists


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
    setup.download(
        set_file_path[1], set_file_path[0] + "downloaded_" + set_file_path[1]
    )
    assert os.path.exists(set_file_path[0] + set_file_path[1])
    os.system(f"rm {set_file_path[0]}downloaded_{set_file_path[1]}")


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
    # file_list = os.popen("osf ls")
    file_list = subprocess.run(
        "$CONDA/bin/" + "osf ls",
        shell=True,
        text=True,
        check=True,
        stdout=subprocess.PIPE,
    ).stdout
    file_list = io.StringIO(file_list)
    line = file_list.readline()
    while line:
        file_exists = set_file_path[1] == line.split("/")[1].strip()
        if file_exists:
            break
        line = file_list.readline()

    assert not file_exists


def test_remove_invalid_because_no_remote_path(setup):
    """Test if an error is raised when no remote_path is provided."""
    with pytest.raises(TypeError):
        setup.remove()
