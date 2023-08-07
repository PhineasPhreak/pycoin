# pycoin
Python wrapper for the [CoinGecko API](https://www.coingecko.com/en/api/documentation) and argparse

# Getting Started
## Prerequisites
This project was written in python. To be able to run this you must have Python 3 installed.
To install the required packages you also need to have **pip** or **pip3** installed.

* `python3-venv` : The venv module provides support for creating lightweight "virtual environments" with their own site directories, optionally isolated from system site directories.

* `python3-pip` : [pip](https://pypi.org/project/pip/) is the Python package installer

Use the `start.sh` script to install the virtual environment and python packages with the `requirements.txt` file.

Use the script `start.sh`
```shell
./start.sh
```

## Creating a virtual Python environment
Using the `python3-venv` package to create the python environment.
```shell
# Creating the 'env' environment
python3 -m venv env
```

## Installation Prerequisites
Used Prerequisites `pandas`, `rich`, `requests` and `pyinstaller`, `pyinstaller-versionfile`
> Documentations :
>
> pandas : [pandas pypi.org](https://pypi.org/project/pandas/) \
> rich : [rich pypi.org](https://pypi.org/project/rich/) \
> requests : [requests pypi.org](https://pypi.org/project/requests/) \
> pyinstaller : [pyinstaller pypi.org](https://pypi.org/project/pyinstaller/) | [pyinstaller manual](https://pyinstaller.org/en/stable/index.html) \
> pyinstaller-versionfile : [pyinstaller-version pypi.org](https://pypi.org/project/pyinstaller-versionfile/)

Install prerequisites and all dependencies
```shell
pip3 install -r requirements.txt
```

# Usage
To start the program simply run :
```shell
python3 pycoin.py
```

## Create a version file from a simple YAML config file
Create a windows version-file from a simple YAML file that can be used by PyInstaller.

Pyinstaller provides a way to capture Windows version data through a so called version-file. The process of crafting such a version file, and especially keeping the version number updated, is a bit cumbersome. This package aims to make the creation of such a version file easier.

### Command line interface
Modify the `versionfile.yml` file with the necessary information.
The encoding must be UTF-8. All fields are optional, you can choose to specify only those that are of interest to you.

To create version-file from this, simple run:

```shell
create-version-file versionfile.yml --outfile file_version_info.txt
```

## Using pyinstaller and pyinstaller-versionfile
PyInstaller bundles a Python application and all its dependencies into a single package. The user can run the packaged app without installing a Python interpreter or any modules.

### Linux
Use the following command :
```shell
# Full command line for Linux
# pyinstaller --onefile --console --name pycoin-linux pycoin.py

pyinstaller pycoin-linux.spec
```

### Windows (Use pyinstaller-versionfile)
Use the following command in the Console (Not Powershell) :
```shell
# Full command line for Windows
# pyinstaller --onefile --console --name pycoin-windows -i src\icon\console-csv.ico --version-file file_version_info.txt pycoin.py

pyinstaller pycoin-windows.spec
```
