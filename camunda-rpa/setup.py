import os
from setuptools import setup, find_packages

setup_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(setup_dir)

setup(
   name='camunda-rpa',
   version='0.1.0',
   description='Exposes RPA libraries under the Camunda namespace',
   author='Camunda Services GmbH',
   author_email='info@camunda.com',
   packages=find_packages(where='Camunda'), 
   package_dir={'': 'Camunda'},
   install_requires=[
      "rpaframework",
      "rpaframework-pdf",
      "rpaframework-windows"
   ], 
)
