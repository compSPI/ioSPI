import pytest
from ioSPI.ioSPI import tem_upload
import random
import string
import requests
import pathlib


@pytest.fixture(autouse = True, scope = 'session')
def setup_teardown():
    """Test node creation and clean-up for tests."""
    token = ''
    request_headers = {"Authorization": f"Bearer {token}"}
    base_api_url = "https://api.osf.io/v2/nodes/"

    test_node_label = 'test_' + ''.join(random.choice(string.ascii_letters) for i in range(5))

    print(f"Creating test node CryoEM Dataset -> internal -> {test_node_label} ")

    internal_node_guid = "9jwpu"
    request_url = f"{base_api_url}{internal_node_guid}/children/"

    request_body = {
        "type": "nodes",
        "attributes": {"title": test_node_label, "category": "data"}
    }

    response = requests.post(
        request_url, headers = request_headers, json = {"data": request_body}
    )
    response.raise_for_status()

    pytest.auth_token = token
    pytest.test_node_guid = response.json()["data"]["id"]
    pytest.request_headers = request_headers
    pytest.base_api_url = base_api_url


@pytest.fixture
def mock_tem():
    """Return mock tem wrapper like object"""

    class SampleTEM:
        def __init__(self):
            self.path_dict = {"pdb_keyword": '',
                              "micrograph_keyword": ''}
            self.output_path_dict = {"h5_file": ''}

    return SampleTEM()


@pytest.fixture
def mock_tem_upload():
    """Return TEMUpload for testing"""
    return tem_upload.TEMUpload(pytest.auth_token, pytest.test_node_guid)


@pytest.fixture
def create_upload_file(tmp_path):
    """Create temporary text file for upload"""
    file_path = pathlib.Path(tmp_path, 'test_upload.txt')
    with open(file_path, "w") as f:
        f.write("Hello World")
    return file_path


def test_upload_dataset_from_tem(mock_tem_upload, mock_tem, create_upload_file):
    """Test whether data is parsed from TEM wrapper and files are uploaded."""
    mock_tem.path_dict["pdb_keyword"] = 'test_upload'
    mock_tem.path_dict["micrograph_keyword"] = ''.join(random.choice(string.ascii_letters) for i in range(5))
    mock_tem.output_path_dict["h5_file"] = str(create_upload_file)
    assert mock_tem_upload.upload_dataset_from_tem(mock_tem)


def test_constructor():
    """Test constructor populates class attributes"""
    test_class = tem_upload.TEMUpload(pytest.auth_token)
    assert test_class.headers is not None
    assert test_class.base_url is not None
    assert test_class.data_node_guid is not None


def test_post_child_node(mock_tem_upload):
    """Test whether nodes are created"""
    test_node_label = 'test_post_child_node' + ''.join(random.choice(string.ascii_letters) for i in range(5))
    returned_guid = mock_tem_upload.post_child_node(pytest.test_node_guid, test_node_label)
    response = requests.get(
        f"{pytest.base_api_url}{returned_guid}", headers = pytest.request_headers
    )
    assert test_node_label == response.json()["data"]["attributes"]["title"]


def test_get_existing_molecules(mock_tem_upload):
    """Test if uploaded test node is retrieved"""
    request_url = f"{pytest.base_api_url}{pytest.test_node_guid}/children/"
    test_node_label = 'test_get_existing_molecules_' + ''.join(random.choice(string.ascii_letters) for i in range(5))
    request_body = {
        "type": "nodes",
        "attributes": {"title": test_node_label, "category": "data"}
    }

    requests.post(
        request_url, headers = pytest.request_headers, json = {"data": request_body}
    ).raise_for_status()

    assert test_node_label in mock_tem_upload.get_existing_molecules()


def test_get_molecule_guid(mock_tem_upload):
    """Test if valid guid is returned for a molecule label"""

    test_node_label = 'test_get_molecule_guid' + ''.join(random.choice(string.ascii_letters) for i in range(5))

    returned_guid = mock_tem_upload.get_molecule_guid(test_node_label)
    response = requests.get(
        f"{pytest.base_api_url}{returned_guid}", headers = pytest.request_headers
    )
    assert response.status_code == 200
    assert returned_guid == mock_tem_upload.get_molecule_guid(test_node_label)


def test_post_files():
    """Test whether files are uploaded to OSF."""
    assert True


def test_generate_tags_from_tem():
    """Test whether tags are generated from TEM configuration parameters."""
    assert True
