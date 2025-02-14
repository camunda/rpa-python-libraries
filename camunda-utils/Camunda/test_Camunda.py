import pytest
import requests
from unittest.mock import patch, Mock
from .Camunda import Camunda


@pytest.fixture
def camunda():
    return Camunda()


# File Upload
@patch("requests.post")
def test_upload_documents_single_file(mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"file1": "descriptor1"}
    mock_post.return_value = mock_response

    result = camunda.upload_documents("file1.txt")
    assert result == "descriptor1"
    assert camunda.outputs == {}


@patch("requests.post")
def test_upload_documents_multiple_files(mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"file1": "descriptor1", "file2": "descriptor2"}
    mock_post.return_value = mock_response

    result = camunda.upload_documents("*.txt")
    assert result == ["descriptor1", "descriptor2"]
    assert camunda.outputs == {}


@patch("requests.post")
def test_upload_documents_with_variable_name(mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"file1": "descriptor1"}
    mock_post.return_value = mock_response

    result = camunda.upload_documents("file1.txt", variableName="fileDescriptor")
    assert result == "descriptor1"
    assert camunda.outputs == {"fileDescriptor": "descriptor1"}


@patch("requests.post")
def test_upload_documents_non_200_response(mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_post.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        camunda.upload_documents("file1.txt")


# File Download
@patch("requests.post")
def test_download_documents_single_file(mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"file1.txt": {"result": "OK"}}
    mock_post.return_value = mock_response

    result = camunda.download_documents({"metadata": {"fileName": "file1.txt"}})
    assert result == "file1.txt"


@patch("requests.post")
def test_download_documents_multiple_files(mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "file1.txt": {"result": "OK"},
        "file2.txt": {"result": "OK"},
    }
    mock_post.return_value = mock_response

    result = camunda.download_documents(
        [
            {"metadata": {"fileName": "file1.txt"}},
            {"metadata": {"fileName": "file2.txt"}},
        ]
    )
    assert result == ["file1.txt", "file2.txt"]


@patch("requests.post")
def test_download_documents_file_not_found(mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "file1.txt": {"result": "OK"},
        "file2.txt": {"result": "NOT_FOUND"},
    }
    mock_post.return_value = mock_response

    with patch("robot.api.logger.warn") as mock_warn:
        result = camunda.download_documents(
            [
                {"metadata": {"fileName": "file1.txt"}},
                {"metadata": {"fileName": "file2.txt"}},
            ]
        )
        assert result == "file1.txt"
        mock_warn.assert_called_with("File file2.txt not found")


@patch("requests.post")
def test_download_documents_non_200_response(mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_post.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        camunda.download_documents({"metadata": {"fileName": "file1.txt"}})


# Roundtrip


@patch("requests.post")
def test_roundtrip_single_file(mock_post, camunda):
    fileDescriptor = {"metadata": {"fileName": "file1.txt"}}

    mock_post_response = Mock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {"file1.txt": fileDescriptor}
    mock_post.return_value = mock_post_response

    descriptors = camunda.upload_documents("file1.txt", variableName="fileDescriptor")

    mock_post_response = Mock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {"file1.txt": {"result": "OK"}}
    mock_post.return_value = mock_post_response

    path = camunda.download_documents(descriptors)
    assert path == "file1.txt"
    assert camunda.outputs == {
        "fileDescriptor": {"metadata": {"fileName": "file1.txt"}}
    }


@patch("requests.post")
def test_roundtrip_single_file(mock_post, camunda):
    file1Descriptor = {"metadata": {"fileName": "file1.txt"}}
    file2Descriptor = {"metadata": {"fileName": "file2.txt"}}

    mock_post_response = Mock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {
        "file1.txt": file1Descriptor,
        "file2.txt": file2Descriptor,
    }
    mock_post.return_value = mock_post_response

    descriptors = camunda.upload_documents("*.txt", variableName="fileDescriptor")

    mock_post_response = Mock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {
        "file1.txt": {"result": "OK"},
        "file2.txt": {"result": "OK"},
    }
    mock_post.return_value = mock_post_response

    paths = camunda.download_documents(descriptors)
    assert paths == ["file1.txt", "file2.txt"]
    assert camunda.outputs == {
        "fileDescriptor": [
            {"metadata": {"fileName": "file1.txt"}},
            {"metadata": {"fileName": "file2.txt"}},
        ]
    }
