from setuptools import setup

setup(
   name='camunda-utils',
   version='0.1.0',
   description='Offer keywords to interact with Camunda from the RPA worker',
   author='Camunda Services GmbH',
   author_email='info@camunda.com',
   packages=[
      'Camunda'
   ], 
   install_requires=[
      "robotframework"
   ], 
)
