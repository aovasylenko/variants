Setup
=====

This guide will help you set up the development environment and get started.

Prerequisites
-------------

- Anaconda or Miniconda installed on your system
- Anaconda-client installed and configured against your `anaconda.org` repository

Steps
-----

1. Create a new conda environment from the provided environment.yml file:
   ```
   conda env create -p ./env -f environment.yml
   ```
   This will create a new environment in with all required dependencies in the `./env` directory.

2. Activate the conda environment:
   ```
   conda activate ./env
   ```

3. Upload your wheel package:
   ```
   python acvar.py upload <wheel path>
   ```
   Replace <wheel path> with the actual path to your .whl file.

Note: Make sure you have the correct permissions and are in the project root directory when running these commands.