import os
from setuptools import setup, find_packages

setup_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(setup_dir)

setup(
    name="camunda-utils",
    version="0.4.0",
    description="Offer keywords to interact with Camunda from the RPA worker",
    author="Camunda Services GmbH",
    author_email="info@camunda.com",
    packages=["Camunda"],
    install_requires=["robotframework"],
)
