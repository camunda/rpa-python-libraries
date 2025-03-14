# Documentation

This directory contains the documentation for the RPA Python Libraries project.

## Build Instructions

To build the documentation, follow these steps:

1. Ensure you have Python and the necessary dependencies installed.
2. Navigate to the `docs` directory:
  ```sh
  cd ./docs
  ```
3. Build the RPA scripts from source
  ```sh
  sh ./build.sh
  ```

## Development

When adding or removing libraries, ensure the changes are reflected in:
  - Update Pages generated in `build.sh`.
  - Update the pages array in `docs/src/js/app.js`.

## View Documentation

You can view the latest version of the documentation on GitHub Pages: [RPA Python Libraries Documentation](https://camunda.github.io/rpa-python-libraries/)