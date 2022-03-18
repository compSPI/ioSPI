"""Tests for osf_upload."""
import os
import random
import string
from pathlib import Path

import pytest
import requests

from ..ioSPI import datasets


@pytest.fixture(autouse=True, scope="session")
def setup_teardown():
    """Test node creation and clean-up for tests."""
    token = os.environ["TEST_TOKEN"]
    print('debugging token')
    print(token)
    request_headers = {"Authorization": f"Bearer {token}"}
    base_api_url = "https://api.osf.io/v2/nodes/"

    test_node_label = "test_" + "".join(
        random.choice(string.ascii_letters) for i in range(5)
    )

    print(f"Creating test node Dataset -> internal -> {test_node_label} ")

    internal_node_guid = "9jwpu"
    request_url = f"{base_api_url}{internal_node_guid}/children/"

    request_body = {
        "type": "nodes",
        "attributes": {"title": test_node_label, "category": "data"},
    }

    response = requests.post(
        request_url, headers=request_headers, json={"data": request_body}
    )
    response.raise_for_status()

    pytest.auth_token = token
    pytest.test_node_guid = response.json()["data"]["id"]
    pytest.test_node_label = test_node_label
    pytest.request_headers = request_headers
    pytest.base_api_url = base_api_url

    yield

    print(
        f"\nDeleting test node Dataset -> internal -> "
        f"{test_node_label} and its sub-components."
    )
    cleanup(pytest.test_node_guid, test_node_label)


def cleanup(node_guid, test_node_label):
    """Recursively delete nodes and subcomponents."""
    base_node_url = f"{pytest.base_api_url}{node_guid}/"

    response = requests.get(f"{base_node_url}children/", headers=pytest.request_headers)
    response.raise_for_status()

    for node_child in response.json()["data"]:
        cleanup(node_child["id"], node_child["attributes"]["title"])

    response = requests.delete(base_node_url, headers=pytest.request_headers)

    if not response.ok:
        print(
            f"Failure: {test_node_label} could not be"
            f" deleted due to error code {response.status_code}."
        )
        print(response.json()["errors"][0]["detail"])
    else:
        print(f"Success: {test_node_label} deleted")


@pytest.fixture
def mock_osf_upload():
    """Return OSFUpload for testing."""
    return datasets.OSFUpload(pytest.auth_token, pytest.test_node_guid)


@pytest.fixture
def create_upload_file(tmp_path):
    """Create temporary text file for upload."""
    file_path = Path(tmp_path, "test_upload_1.txt")
    with open(file_path, "w") as f:
        f.write("Hello World")
    return file_path


def test_constructor():
    """Test constructor populates class attributes."""
    test_class = datasets.OSFUpload(pytest.auth_token)

    assert test_class.headers is not None
    assert test_class.base_url is not None
    assert test_class.data_node_guid is not None


def test_write_child_node(mock_osf_upload):
    """Test whether nodes are created."""
    test_node_label = "test_write_child_node" + "".join(
        random.choice(string.ascii_letters) for i in range(5)
    )
    returned_guid = mock_osf_upload.write_child_node(
        pytest.test_node_guid, test_node_label
    )
    response = requests.get(
        f"{pytest.base_api_url}{returned_guid}", headers=pytest.request_headers
    )
    assert test_node_label == response.json()["data"]["attributes"]["title"]


def test_read_existing_structure_labels(mock_osf_upload):
    """Test if uploaded test node is retrieved."""
    request_url = f"{pytest.base_api_url}{pytest.test_node_guid}/children/"
    test_node_label = "test_read_existing_structure_labels_" + "".join(
        random.choice(string.ascii_letters) for i in range(5)
    )
    request_body = {
        "type": "nodes",
        "attributes": {"title": test_node_label, "category": "data"},
    }

    requests.post(
        request_url, headers=pytest.request_headers, json={"data": request_body}
    ).raise_for_status()

    assert test_node_label in mock_osf_upload.read_existing_structure_labels()


def test_read_structure_guid(mock_osf_upload):
    """Test if valid guid is returned for a structure's label."""
    test_node_label = "test_read_structure_guid" + "".join(
        random.choice(string.ascii_letters) for i in range(5)
    )

    returned_guid = mock_osf_upload.read_structure_guid(test_node_label)
    assert returned_guid is None

    request_url = f"{pytest.base_api_url}{pytest.test_node_guid}/children/"
    request_body = {
        "type": "nodes",
        "attributes": {"title": test_node_label, "category": "data", "public": True},
    }
    response = requests.post(
        request_url, headers=pytest.request_headers, json={"data": request_body}
    )
    response.raise_for_status()

    assert response.json()["data"]["id"] == mock_osf_upload.read_structure_guid(
        test_node_label
    )


def test_write_files(mock_osf_upload, create_upload_file):
    """Test whether files are uploaded to OSF."""
    assert mock_osf_upload.write_files(pytest.test_node_guid, [str(create_upload_file)])

    response = requests.get(
        f"{pytest.base_api_url}{pytest.test_node_guid}/files/osfstorage/",
        headers=pytest.request_headers,
    )

    response.raise_for_status()
    parsed_response = response.json()["data"][0]

    assert Path(create_upload_file).name == parsed_response["attributes"]["name"]
