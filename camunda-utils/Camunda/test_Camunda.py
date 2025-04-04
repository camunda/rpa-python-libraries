import pytest
import requests
import json
from unittest.mock import patch, Mock, MagicMock

from requests import HTTPError
from robot.libraries.BuiltIn import BuiltIn

from .Camunda import Camunda, Secrets


# Secret mapping


# Test for Secrets class
def test_secrets_retrieval():
    secrets_dict = {"KEY1": "value1", "KEY2": "value2"}
    secrets = Secrets(secrets_dict)

    assert secrets.KEY1 == "value1"
    assert secrets.KEY2 == "value2"


def test_secrets_non_existent_key():
    secrets_dict = {"KEY1": "value1"}
    secrets = Secrets(secrets_dict)

    with pytest.raises(KeyError):
        _ = secrets.KEY2


@patch(
    "os.environ",
    {"CAMUNDA_SECRETS": '{"KEY1": "value1", "KEY2": "value2"}'},
)
@patch("robot.libraries.BuiltIn.BuiltIn.get_variable_value", return_value=None)
@patch("robot.libraries.BuiltIn.BuiltIn.set_global_variable")
def test_secret_mapping(mock_set_global_variable, mock_get_variable_value):
    camunda = Camunda()

    mock_set_global_variable.assert_called_with(
        "${secrets}", {"KEY1": "value1", "KEY2": "value2"}
    )

    # Assert access via attributes
    SECRETS = mock_set_global_variable.call_args[0][1]

    assert SECRETS.KEY1 == "value1"
    assert SECRETS.KEY2 == "value2"


@patch("os.environ", {})
@patch("robot.libraries.BuiltIn.BuiltIn.get_variable_value", return_value=None)
@patch("robot.libraries.BuiltIn.BuiltIn.set_global_variable")
def test_secret_mapping_no_secrets(mock_set_global_variable, mock_get_variable_value):
    camunda = Camunda()
    mock_set_global_variable.assert_not_called()


@patch("os.environ", {"SECRET_KEY1": "value1"})
@patch(
    "robot.libraries.BuiltIn.BuiltIn.get_variable_value",
    return_value={"EXISTING_KEY": "existing_value"},
)
@patch("robot.libraries.BuiltIn.BuiltIn.set_global_variable")
def test_secret_mapping_existing_variable(
    mock_set_global_variable, mock_get_variable_value
):
    camunda = Camunda()
    mock_set_global_variable.assert_not_called()


# Worker configuration


# Uses default BaseURL
@patch(
    "os.environ",
    {
        "RPA_WORKSPACE_ID": "workspace_id",
    },
)
@patch("requests.post")
def test_default_base_url(mock_post):
    camunda = Camunda()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"file1": "descriptor1"}
    mock_post.return_value = mock_response

    camunda.upload_documents("file1.txt")

    assert mock_post.call_args[0][0] == "http://127.0.0.1:36227/file/store/workspace_id"


# With BaseURL
@patch(
    "os.environ",
    {
        "RPA_WORKSPACE_ID": "workspace_id",
        "RPA_BASE_URL": "http://rpa-worker:12345",
    },
)
@patch("requests.post")
def test_custom_base_url(mock_post):
    camunda = Camunda()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"file1": "descriptor1"}
    mock_post.return_value = mock_response

    camunda.upload_documents("file1.txt")

    assert (
        mock_post.call_args[0][0] == "http://rpa-worker:12345/file/store/workspace_id"
    )


### BPMN Error


# Throw error without variables
@patch("requests.post")
@patch("os.environ", {"RPA_ZEEBE_JOB_KEY": "12345"})
def test_throw_bpmn_error(mock_post):
    camunda = Camunda()
    mock_response = Mock()
    mock_response.status_code = 202
    mock_post.return_value = mock_response

    with pytest.raises(Exception, match="ERROR_CODE - Error message") as excinfo:
        camunda.throw_bpmn_error("ERROR_CODE", "Error message")

    mock_post.assert_called_once_with(
        "http://127.0.0.1:36227/zeebe/job/12345/throw",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "errorCode": "ERROR_CODE",
                "errorMessage": "Error message",
            }
        ),
    )

    assert excinfo.value.ROBOT_EXIT_ON_FAILURE is True


# Throw error without errorMessage
@patch("requests.post")
@patch("os.environ", {"RPA_ZEEBE_JOB_KEY": "12345"})
def test_throw_bpmn_error_no_message(mock_post):
    camunda = Camunda()
    mock_response = Mock()
    mock_response.status_code = 202
    mock_post.return_value = mock_response

    with pytest.raises(
        Exception, match="ERROR_CODE - No error message provided"
    ) as excinfo:
        camunda.throw_bpmn_error("ERROR_CODE")

    mock_post.assert_called_with(
        "http://127.0.0.1:36227/zeebe/job/12345/throw",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "errorCode": "ERROR_CODE",
            }
        ),
    )

    assert excinfo.value.ROBOT_EXIT_ON_FAILURE is True


# Throw error with variables
@patch("requests.post")
@patch("os.environ", {"RPA_ZEEBE_JOB_KEY": "12345"})
def test_throw_bpmn_error_variables(mock_post):
    camunda = Camunda()
    mock_response = Mock()
    mock_response.status_code = 202
    mock_post.return_value = mock_response

    with pytest.raises(Exception, match="ERROR_CODE - Error message") as excinfo:
        camunda.set_output_variable("output1", "value1")
        camunda.set_output_variable("output2", "value2")

        camunda.throw_bpmn_error(
            "ERROR_CODE",
            errorMessage="Error message",
            variables={
                "errorVar1": "value1",
                "errorVar2": "value2",
            },
        )

    mock_post.assert_called_with(
        "http://127.0.0.1:36227/zeebe/job/12345/throw",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "errorCode": "ERROR_CODE",
                "errorMessage": "Error message",
                "variables": {
                    "errorVar1": "value1",
                    "errorVar2": "value2",
                },
            }
        ),
    )

    assert excinfo.value.ROBOT_EXIT_ON_FAILURE is True


@patch("requests.post")
def test_throw_bpmn_error_handle_stubbed_response(mock_post):
    # given:
    camunda = Camunda()
    mock_response = MagicMock()
    mock_response.status_code = 501
    mock_response.raise_for_status = Mock(side_effect=HTTPError())
    mock_post.return_value = mock_response

    # when:
    with pytest.raises(Exception, match="ERROR_CODE - Error message") as excinfo:
        camunda.throw_bpmn_error("ERROR_CODE", "Error message")

    # then:
    mock_post.assert_called_once_with(
        "http://127.0.0.1:36227/zeebe/job/-1/throw",
        headers={'Content-Type': 'application/json'},
        data='{"errorCode": "ERROR_CODE", "errorMessage": "Error message"}')
    
    # and:
    assert excinfo.value.ROBOT_EXIT_ON_FAILURE is True


### File Handling
@pytest.fixture
def camunda():
    with patch("robot.libraries.BuiltIn.BuiltIn.get_variable_value"), patch(
        "robot.libraries.BuiltIn.BuiltIn.set_global_variable"
    ):
        return Camunda()


# File Upload
@patch("requests.post")
@patch.object(Camunda, "set_output_variable")
def test_upload_documents_single_file(mock_set_output_variable, mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"file1": "descriptor1"}
    mock_post.return_value = mock_response

    result = camunda.upload_documents("file1.txt")
    assert result == ["descriptor1"]
    mock_set_output_variable.assert_not_called()


@patch("requests.post")
@patch.object(Camunda, "set_output_variable")
def test_upload_documents_multiple_files(mock_set_output_variable, mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"file1": "descriptor1", "file2": "descriptor2"}
    mock_post.return_value = mock_response

    result = camunda.upload_documents("*.txt")
    assert result == ["descriptor1", "descriptor2"]
    mock_set_output_variable.assert_not_called()


@patch("requests.post")
@patch.object(Camunda, "set_output_variable")
def test_upload_documents_with_variable_name(
    mock_set_output_variable, mock_post, camunda
):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"file1": "descriptor1"}
    mock_post.return_value = mock_response

    result = camunda.upload_documents("file1.txt", variableName="fileDescriptor")
    assert result == ["descriptor1"]
    mock_set_output_variable.assert_called_once_with("fileDescriptor", ["descriptor1"])


@patch("requests.post")
def test_upload_documents_non_200_response(mock_post, camunda):
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_post.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        camunda.upload_documents("file1.txt")

@patch("requests.post")
def test_upload_documents_handle_stubbed_response(mock_post):
    # given:
    camunda = Camunda()
    mock_response = MagicMock()
    mock_response.status_code = 501
    mock_response.raise_for_status = Mock(side_effect=HTTPError())
    mock_post.return_value = mock_response

    # expect:
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


@patch("requests.post")
@patch("robot.libraries.BuiltIn.BuiltIn.fatal_error")
def test_download_documents_handle_stubbed_response(mock_fatal_error, mock_post):
    # given:
    camunda = Camunda()
    
    mock_response = Mock()
    mock_response.status_code = 501
    mock_response.raise_for_status = Mock(side_effect=HTTPError())
    mock_response.json.return_value = {"target": "DocumentClient", "action": "getDocuments", "request":{}}
    mock_post.return_value = mock_response
    
    # and:
    mock_fatal_error.side_effect = AssertionError()

    # when:
    with(pytest.raises(AssertionError)):
        camunda.download_documents({"metadata": {"fileName": "file1.txt"}})
    
    # then:
    mock_fatal_error.assert_called_once()

# Roundtrip


@patch("requests.post")
@patch.object(Camunda, "set_output_variable")
def test_roundtrip_single_file(mock_set_output_variable, mock_post, camunda):
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
    mock_set_output_variable.assert_called_once_with(
        "fileDescriptor", {"metadata": {"fileName": "file1.txt"}}
    )


@patch("requests.post")
@patch.object(Camunda, "set_output_variable")
def test_roundtrip_single_file(mock_set_output_variable, mock_post, camunda):
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
    mock_set_output_variable.assert_called_once_with(
        "fileDescriptor",
        [
            {"metadata": {"fileName": "file1.txt"}},
            {"metadata": {"fileName": "file2.txt"}},
        ],
    )


@patch("requests.post")
@patch("os.environ", {"RPA_WORKSPACE_ID": "workspace_id"})
def test_set_output_variable_success(mock_post):
    camunda = Camunda()

    mock_response = Mock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    camunda.set_output_variable("result", "Hello, World!")

    mock_post.assert_called_once_with(
        "http://127.0.0.1:36227/workspace/workspace_id/variables",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "variables": {
                    "result": "Hello, World!",
                }
            }
        ),
    )


@patch("requests.post")
@patch("os.environ", {"RPA_WORKSPACE_ID": "workspace_id"})
def test_set_output_variable_failure(mock_post):
    camunda = Camunda()

    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError
    mock_post.return_value = mock_response

    with pytest.raises(requests.exceptions.HTTPError):
        camunda.set_output_variable("result", "Hello, World!")

    mock_post.assert_called_once_with(
        "http://127.0.0.1:36227/workspace/workspace_id/variables",
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "variables": {
                    "result": "Hello, World!",
                }
            }
        ),
    )
