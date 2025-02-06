import yaml
import os
import mimetypes
import base64

from robot.api.deco import keyword


class Camunda:
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.ROBOT_LIBRARY_LISTENER = self
        self.outputs = {}

    @keyword(name="Set Output Variable")
    def set_output_variable(self, name, value):
        """
        Stores the value in-memory with the name as key.
        """
        self.outputs[name] = value

    @keyword(name="Set Output File")
    def set_output_file(self, name, path):
        """
        Parses the file at `path` using `create_file_object` and stores the return value in-memory with the name as a key.
        """
        try:
            # Assuming create_file_object is a function you've written elsewhere
            file_object = create_file_object(path)
            self.outputs[name] = file_object
        except Exception as e:
            raise Exception(f"Failed to parse file and set output: {e}")

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


def create_file_object(path):
    # This is a placeholder for the actual file parsing logic.
    # Replace this with the actual implementation.
    print(f"create_file_object {path}")

    if os.path.isfile(path):
        file_name = os.path.basename(path)
        file_name = file_name.replace(".", "_")
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type and mime_type.startswith("image/"):
            content = file_to_data_url(path)
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        return content


def file_to_data_url(file_path):
    """
    Convert an image file to a data URL.
    """
    print(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)
    with open(file_path, "rb", encoding="UTF8") as f:
        encoded_string = base64.b64encode(f.read()).decode("utf-8")
        data_url = f"data:{mime_type};base64,{encoded_string}"
    return data_url
