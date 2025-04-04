import requests
import json
import yaml
import os
import mimetypes
import base64

from typing import Any, List, Optional, Union, Dict
from robot.api.deco import keyword
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

SECRET_VARIABLE = "${secrets}"
SECRET_ENV_NAME = "CAMUNDA_SECRETS"


class Secrets(dict):
    """
    A wrapper around a dictionary that allows access to the values via attributes.
    This allows access as `${SECRETS.key}` instead of `${SECRETS['key']}`
    """

    def __getattr__(self, name):
        return self[name]


class Camunda:
    """
    A Robot Framework library that provides keywords to interact with Camunda from the RPA worker.
    """

    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_DOC_FORMAT = "REST"

    def __init__(self):
        self.workspace_id = os.getenv("RPA_WORKSPACE_ID")
        self.job_key = os.getenv("RPA_ZEEBE_JOB_KEY")
        self.base_url = os.getenv("RPA_BASE_URL", "http://127.0.0.1:36227")
        self.ROBOT_LIBRARY_LISTENER = self

        self._map_secrets()

    def _map_secrets(self):
        """
        Secrets are provided as a JSON object in the environment variable 'CAMUNDA_SECRETS'.
        For easy access, we want to provide them as a robot variable instead.
        """

        # Get secrets from the environment variable
        secrets_json = os.getenv(SECRET_ENV_NAME)

        if not secrets_json:
            return

        built_in = BuiltIn()

        existing_secrets = built_in.get_variable_value("${SECRETS}")

        # Do not overwrite existing secrets
        if existing_secrets:
            return

        secrets = json.loads(secrets_json)
        secrets_wrapper = Secrets(secrets)

        # Set Robot variable
        built_in.set_global_variable(SECRET_VARIABLE, secrets_wrapper)

    @keyword(name="Throw BPMN Error")
    def throw_bpmn_error(
        self,
        errorCode: str,
        errorMessage: Optional[str] = None,
        variables: Optional[Dict[str, Any]] = None,
    ):
        """Create a BPMN error and end script execution.

        Your BPMN process should contain an error catch event to handle this error. Learn more about BPMN errors in the `Camunda docs`_.

        :param errorCode: The error code to throw.
        :param errorMessage: The error message to throw. Defaults to None.
        :param variables: A dictionary of variables to pass to the error event. Defaults to None.

        .. _Camunda docs: https://docs.camunda.io/docs/components/best-practices/development/dealing-with-problems-and-exceptions/#handling-errors-on-the-process-level
        """
        url = f"{self.base_url}/zeebe/job/{self.job_key or -1}/throw"
        headers = {"Content-Type": "application/json"}

        data = {
            "errorCode": errorCode,
        }

        if errorMessage:
            data["errorMessage"] = errorMessage

        if variables:
            data["variables"] = variables

        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        self._check_response(response, 202)

        # Stop the script execution and only do teardown after this keyword
        BuiltIn().fatal_error(
            f"{errorCode} - {errorMessage or 'No error message provided'}"
        )

    @keyword(name="Set Output Variable")
    def set_output_variable(self, name, value):
        """Sets the output variable of the Task in the calling process.

        :param name: The name of the output variable.
        :param value: The value of the output variable.

        Examples:

        .. code-block:: robotframework

            # Set the output variable 'result' to the value 'Hello, World!'
            Set Output Variable    result    Hello, World!

            # Set output variable 'result' to the value of the variable ${output}
            Set Output Variable    result    ${output}
        """

        url = f"{self.base_url}/workspace/{self.workspace_id}/variables"
        headers = {"Content-Type": "application/json"}

        data = {
            "variables": {
                name: value,
            }
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code != 200:
            response.raise_for_status()

    @keyword
    def upload_documents(self, glob: str, variableName: Optional[str] = None):
        """Upload a document to Camunda. Optionaly store the file descriptor in an output variable.

        :param glob: A glob pattern with files to upload.
        :param variableName: The name of the variable to store the file descriptor in.
        :return: A file descriptor or a list of file descriptors of the uploaded documents.

        Examples:

        .. code-block:: robotframework

            # Upload a single file
            ${fileDescriptor}=   Upload Document    path/to/file.txt
            Set Output Variable    fileDescriptor    ${fileDescriptor}

            # Directly store the file descriptor in a variable
            Upload Document    path/to/file.txt     variableName="fileDescriptor"

            # Upload all files in a directory
            Upload Document    path/to/directory/*   variableName="invoices"

            # Upload all .pdf files in the workspace
            Upload Document    *.pdf   variableName="pdfs"
        """
        url = f"{self.base_url}/file/store/{self.workspace_id}"
        headers = {"Content-Type": "application/json"}

        data = {"files": glob}

        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        self._check_response(response, 200)
        
        fileDescriptors = list(response.json().values())

        if variableName:
            self.set_output_variable(variableName, fileDescriptors)

        return fileDescriptors

    @keyword
    def download_documents(self, fileDescriptor, path: Optional[str] = "") -> List[str]:
        """Retrieve one or multiple documents from the backend.

        :param fileDescriptor: The file descriptor of the document to retrieve.
        :param path: The path where the document should be saved to. Defaults to the workspace directory.
        :return: A path or a list of paths to the downloaded files.

        Examples:

        .. code-block::  robotframework

            # Downloads documents into `input` directory
            ${inputFiles} =    Download Document    ${fileDescriptor}    input

            # Downloads a single document into the workspace directory
            ${inputFile} =    Download Document    ${fileDescriptor}
        """

        if isinstance(fileDescriptor, dict):
            fileDescriptor = [fileDescriptor]

        # Transform fileDescriptor to a list of file descriptors
        fileDescriptor = {
            os.path.join(path, file["metadata"]["fileName"]): file
            for file in fileDescriptor
        }

        url = f"{self.base_url}/file/retrieve/{self.workspace_id}"
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, headers=headers, data=json.dumps(fileDescriptor))

        self._check_response(response, 200, 
                             lambda ignored: BuiltIn().fatal_error("Cannot continue after stub call to Download Documents"))

        downloadedFiles = [
            file for file, result in response.json().items() if result["result"] == "OK"
        ]
        notFoundFiles = [
            file
            for file, result in response.json().items()
            if result["result"] == "NOT_FOUND"
        ]

        for file in notFoundFiles:
            logger.warn(f"File {file} not found")

        # If we only have 1 file, return the file path as a string
        if len(downloadedFiles) == 1:
            return downloadedFiles[0]

        return downloadedFiles
    
    def _check_response(self, response, expected, stub_handler = (lambda r: None)):
        if response.status_code == 501:
            return self._handle_stub_response(response, stub_handler)
        if response.status_code != expected:
            response.raise_for_status()
        
    def _handle_stub_response(self, response, stub_handler):
        logger.info(f"STUB: {response.json()['target']}→{response.json()['action']}\n" +
                    json.dumps(dict(response.json()['request']), indent=4))
        stub_handler(response)
