# pycoin
Python wrapper for the [CoinGecko API](https://www.coingecko.com/en/api/documentation) and argparse

# Getting Started
## Prerequisites
This project was written in python. To be able to run this you must have Python 3 installed.
To install the required packages you also need to have **pip** or **pip3** installed.

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

**OR**, use the script `start.sh`
```shell
./start.sh
```

# Usage
To start the program simply run :
```shell
python3 pycoin.py
```

## Using pyinstaller and pyinstaller-versionfile
Create a windows version-file from a simple YAML file that can be used by PyInstaller.

Pyinstaller provides a way to capture Windows version data through a so called version-file. The process of crafting such a version file, and especially keeping the version number updated, is a bit cumbersome. This package aims to make the creation of such a version file easier.

## Linux
Use the following command :
```shell
# Full command line for Linux
# pyinstaller --onefile --console --name pycoin-linux pycoin.py

pyinstaller pycoin-linux.spec
```

## Windows (Use pyinstaller-versionfile)
Use the following command in the Console (Not Powershell) :
```shell
# Full command line for Windows
# pyinstaller --onefile --console --name pycoin-windows -i src\icon\console-csv.ico --version-file file_version_info.txt pycoin.py

pyinstaller pycoin-windows.spec
```
