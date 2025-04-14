import os
from setuptools import setup, find_packages

setup_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(setup_dir)

setup(
    packages=["Camunda"],
)
