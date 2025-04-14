import os
from setuptools import setup, find_packages

setup_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(setup_dir)

setup(
    packages=[
        "Camunda.Archive",
        "Camunda.Browser.Selenium",
        "Camunda.Calendar",
        "Camunda.Desktop",
        "Camunda.Desktop.OperatingSystem",
        "Camunda.Excel.Application",
        "Camunda.Excel.Files",
        "Camunda.FileSystem",
        "Camunda.FTP",
        "Camunda.HTTP",
        "Camunda.Images",
        "Camunda.JavaAccessBridge",
        "Camunda.JSON",
        "Camunda.MFA",
        "Camunda.MSGraph",
        "Camunda.Outlook.Application",
        "Camunda.PDF",
        "Camunda.SAP",
        "Camunda.Tables",
        "Camunda.Tasks",
        "Camunda.Windows",
        "Camunda.Word.Application",
    ],
)
