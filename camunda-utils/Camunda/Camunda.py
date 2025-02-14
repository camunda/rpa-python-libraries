import requests
import json
import yaml
import os
import mimetypes
import base64

from typing import Any, List, Optional, Union, Dict
from robot.api.deco import keyword
from robot.api import logger


class Camunda:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LISTENER_API_VERSION = 2
    ROBOT_LIBRARY_DOC_FORMAT = "REST"

    def __init__(self):
        self.workspace_id = os.getenv("RPA_WORKSPACE_ID")
        self.base_url = "http://localhost:36227"
        self.ROBOT_LIBRARY_LISTENER = self
        self.outputs = {}

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
        self.outputs[name] = value

    @keyword
    def upload_documents(self, glob: str, variableName: Optional[str] = None):
        """Upload a document to Camunda. Optionaly store the file descriptor in an output variable.

        :param glob: A glob pattern with files to upload.
        :param variableName: The name of the variable to store the file descriptor in.
        :return: A file descriptor or a list of file descriptors of the uploaded documents.

        Examples:

        .. code-block:: robotframework

            # Upload a single file
            Upload Document    path/to/file.txt
            Set Output Variable    fileDescriptor    ${fileDescriptor}

            # Directly store the file descriptor in a variable
            Upload Document    path/to/file.txt

            # Upload all files in a directory
            Upload Document    path/to/directory/*   variableName="invoices"

            # Upload all .pdf files in the workspace
            Set Output Variable    fileDescriptor    variableName="invoices"
        """
        url = f"{self.base_url}/file/store/{self.workspace_id}"
        headers = {"Content-Type": "application/json"}

        data = {"files": glob}

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code != 200:
            response.raise_for_status()

        fileDescriptors = list(response.json().values())

        # If we only have 1 file, return the file descriptor as a string
        if len(fileDescriptors) == 1:
            fileDescriptors = fileDescriptors[0]

        if variableName:
            self.outputs[variableName] = fileDescriptors

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

        if response.status_code != 200:
            response.raise_for_status()

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

    def _write_outputs_to_file(self):
        """
        Writes the current state of self.outputs to 'outputs.yml'.
        """
        with open("outputs.yml", "w", encoding="UTF8") as outfile:
            yaml.dump(self.outputs, outfile, default_flow_style=False)

    def _close(self):
        """
        A listener method that is called after the test suite has finished execution.
        """
        self._write_outputs_to_file()
