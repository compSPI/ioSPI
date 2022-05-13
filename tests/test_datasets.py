"""Unit tests for listing/uploading/downloading datasets on an OSF project."""

import os

import pytest

from ioSPI import datasets


@pytest.fixture(autouse=True, scope="session")
def setup():
    """Test node creation and clean-up for tests."""
    print(f"Creating a test project for dataset")
    project = datasets.OSFProject(
        username="ninamio78@gmail.com",
        token="HBGGBOJcLYQfadEKIOyXJiLTum3ydXK4nGP3KmbkYUeBuYkZma9LPBSYennQn92gjP2NHn",
        project_id="xbr2m",
    )

    yield project


@pytest.fixture
def create_upload_file():
    """Create a temporary text file for upload."""
    file_path = "test_upload.txt"
    with open(file_path, "w") as f:
        f.write("Hello World")
    return file_path


def test_constructor_valid():
    """Test the constructor."""
    project = datasets.OSFProject(username="username", token="token")
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


def test_upload_valid(setup, create_upload_file):
    """Test the upload method."""
    setup.upload(create_upload_file, create_upload_file)
    out = os.popen("osf ls").read()
    file_exists = False
    for file in out:
        file_exists = create_upload_file == file.split("/")[1]

    assert file_exists


def test_upload_invalid_because_no_local_path(setup):
    """Test if an error is raised when no local_path is provided."""
    with pytest.raises(TypeError):
        setup.upload(remote_path="remote_path")


def test_upload_invalid_because_no_remote_path(setup):
    """Test if an error is raised when no remote_path is provided."""
    with pytest.raises(TypeError):
        setup.upload(local_path="local_path")


def test_download_valid(setup, create_upload_file):
    """Test the download method."""
    setup.download(create_upload_file, create_upload_file)
    assert os.path.exists(create_upload_file)


def test_download_invalid_because_no_remote_path(setup):
    """Test if an error is raised when no remote_path is provided."""
    with pytest.raises(TypeError):
        setup.download(local_path="local_path")


def test_download_invalid_because_no_local_path(setup):
    """Test if an error is raised when no local_path is provided."""
    with pytest.raises(TypeError):
        setup.download(remote_path="remote_path")


def test_remove_valid(setup, create_upload_file):
    """Test the remove method."""
    setup.remove(create_upload_file)
    out = os.popen("osf ls").read()
    file_exists = False
    for file in out:
        file_exists = create_upload_file == file.split("/")[1]

    assert not file_exists


def test_remove_invalid_because_no_remote_path(setup):
    """Test if an error is raised when no remote_path is provided."""
    with pytest.raises(TypeError):
        setup.remove()
