"""Tests for tem_upload."""
import os
import random
import string
from pathlib import Path

import pytest
import requests
import tem

from ioSPI.ioSPI import tem_upload


@pytest.fixture(autouse = True, scope = "session")
def setup_teardown():
    """Test node creation and clean-up for tests."""
    token = os.environ["TEST_TOKEN"]
    request_headers = {"Authorization": f"Bearer {token}"}
    base_api_url = "https://api.osf.io/v2/nodes/"

    test_node_label = "test_" + "".join(
        random.choice(string.ascii_letters) for i in range(5)
    )

    print(f"Creating test node CryoEM Dataset -> internal -> {test_node_label} ")

    internal_node_guid = "9jwpu"
    request_url = f"{base_api_url}{internal_node_guid}/children/"

    request_body = {
        "type": "nodes",
        "attributes": {"title": test_node_label, "category": "data"},
    }

    response = requests.post(
        request_url, headers = request_headers, json = {"data": request_body}
    )
    response.raise_for_status()

    pytest.auth_token = token
    pytest.test_node_guid = response.json()["data"]["id"]
    pytest.test_node_label = test_node_label
    pytest.request_headers = request_headers
    pytest.base_api_url = base_api_url

    yield

    print(
        f"\nDeleting test node CryoEM Dataset -> internal -> "
        f"{test_node_label} and its sub-components."
    )
    cleanup(pytest.test_node_guid, test_node_label)


def cleanup(node_guid, test_node_label):
    """Recursively delete nodes and subcomponents."""
    base_node_url = f"{pytest.base_api_url}{node_guid}/"

    response = requests.get(f"{base_node_url}children/", headers = pytest.request_headers)
    response.raise_for_status()

    for node_child in response.json()["data"]:
        cleanup(node_child["id"], node_child["attributes"]["title"])

    response = requests.delete(base_node_url, headers = pytest.request_headers)

    if not response.ok:
        print(
            f"Failure: {test_node_label} could not be"
            f" deleted due to error code {response.status_code}."
        )
        print(response.json()["errors"][0]["detail"])
    else:
        print(f"Success: {test_node_label} deleted")


@pytest.fixture
def mock_tem(tmp_path):
    """Instantiate TEMSimulator for testing."""
    test_files_path = "./test_files"
    cwd = os.getcwd()

    tem_simulator = tem.TEMSimulator(
        str(Path(cwd, test_files_path, "path_config.yaml")),
        str(Path(cwd, test_files_path, "sim_config.yaml")),
    )

    # from test_files/path_config
    out_file_name = "_randomrot"

    tem_simulator.output_path_dict["mrc_file"] = str(
        Path(cwd, tmp_path, out_file_name + ".mrc")
    )

    tem_simulator.output_path_dict["pdb_file"] = str(
        Path(cwd, test_files_path, "4v6x.pdb")
    )

    return tem_simulator


@pytest.fixture
def mock_tem_upload():
    """Return TEMUpload for testing."""
    return tem_upload.TEMUpload(pytest.auth_token, pytest.test_node_guid)


@pytest.fixture
def create_upload_file(tmp_path):
    """Create temporary text file for upload."""
    file_path = Path(tmp_path, "test_upload_1.txt")
    with open(file_path, "w") as f:
        f.write("Hello World")
    return file_path


def test_constructor():
    """Test constructor populates class attributes."""
    test_class = tem_upload.TEMUpload(pytest.auth_token)

    assert test_class.headers is not None
    assert test_class.base_url is not None
    assert test_class.data_node_guid is not None


def test_upload_dataset_from_tem(mock_tem_upload, mock_tem, create_upload_file):
    """Test whether data is parsed from TEM wrapper and files are uploaded."""
    mock_tem.output_path_dict["h5_file"] = str(create_upload_file)
    assert mock_tem_upload.upload_dataset_from_tem(mock_tem)


def test_post_child_node(mock_tem_upload):
    """Test whether nodes are created."""
    test_node_label = "test_post_child_node" + "".join(
        random.choice(string.ascii_letters) for i in range(5)
    )
    returned_guid = mock_tem_upload.post_child_node(
        pytest.test_node_guid, test_node_label
    )
    response = requests.get(
        f"{pytest.base_api_url}{returned_guid}", headers = pytest.request_headers
    )
    assert test_node_label == response.json()["data"]["attributes"]["title"]


def test_get_existing_molecules(mock_tem_upload):
    """Test if uploaded test node is retrieved."""
    request_url = f"{pytest.base_api_url}{pytest.test_node_guid}/children/"
    test_node_label = "test_get_existing_molecules_" + "".join(
        random.choice(string.ascii_letters) for i in range(5)
    )
    request_body = {
        "type": "nodes",
        "attributes": {"title": test_node_label, "category": "data"},
    }

    requests.post(
        request_url, headers = pytest.request_headers, json = {"data": request_body}
    ).raise_for_status()

    assert test_node_label in mock_tem_upload.get_existing_molecules()


def test_get_molecule_guid(mock_tem_upload):
    """Test if valid guid is returned for a molecule label."""
    test_node_label = "test_get_molecule_guid" + "".join(
        random.choice(string.ascii_letters) for i in range(5)
    )

    returned_guid = mock_tem_upload.get_molecule_guid(test_node_label)
    response = requests.get(
        f"{pytest.base_api_url}{returned_guid}", headers = pytest.request_headers
    )
    assert response.status_code == 200
    assert returned_guid == mock_tem_upload.get_molecule_guid(test_node_label)


def test_post_files(mock_tem_upload, create_upload_file):
    """Test whether files are uploaded to OSF."""
    assert mock_tem_upload.post_files(pytest.test_node_guid, [str(create_upload_file)])

    response = requests.get(
        f"{pytest.base_api_url}{pytest.test_node_guid}/files/osfstorage/",
        headers = pytest.request_headers,
    )

    response.raise_for_status()
    parsed_response = response.json()["data"][0]

    assert Path(create_upload_file).name == parsed_response["attributes"]["name"]


def test_generate_tags_from_tem(mock_tem,mock_tem_upload):
    print("\n")
    print(mock_tem_upload.generate_tags_from_tem(mock_tem))
    assert True
