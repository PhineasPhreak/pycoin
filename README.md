# pycoin
Python wrapper for the [CoinGecko API](https://www.coingecko.com/en/api/documentation) and [argparse](https://docs.python.org/3/library/argparse.html)

# Preview options
```
usage: pycoin.py [-h] [-n str] [-e str [str ...]] [-P] [-C] [-p int] [-t int] [-c str] [-E] [-g] [-G] [-T] [-H bitcoin, ethereum] [-V] [-v]

Use of the CoinGecko API by generating a CSV, HTML AND JSON file, with the non-exhaustive list of Cryptocurrency.

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         increase output visibility

  -n str, --name str    Define output file name. default 'markets'

  -e str [str ...], --extension str [str ...]
                        Selects CSV, HTML and JSON output file extensions

Status Server:
  -P, --ping            check API server status

Coins List:
  -C, --coins_list      List all coins with id, name, and symbol. All the coins that show up on this /coins/list endpoint are Active coins that listed by
                        CoinGecko team on CoinGecko.com. If a coin is inactive or deactivated, it will be removed from /coins/list

Options Markets:
  -p int, --page int    Customization of the number of pages to generate in the *.csv, do not exceed 15 for the page generation value
  -t int, --time int    Define waiting time in seconds between each request, Avoid values below 5 seconds (default is 25 seconds)
  -c str, --currency str
                        Choose the type of currency we want, USD being the default currency. Choice: usd, eur, cad, gbp, etc

Options Exchanges:
  -E, --exchanges       List all exchanges (Active with trading volumes)

Get cryptocurrency global data:
  -g, --global          Get global data - total_volume, total_market_cap, ongoing icos etc
  -G, --global_defi     Get Top 100 Cryptocurrency Global Eecentralized Finance(defi) data

Get Top-7 trending coins:
  -T, --trending        Top-7 trending coins on CoinGecko as searched by users in the last 24 hours (Ordered by most popular first).

Get public companies data (beta):
  -H bitcoin, ethereum, --companies bitcoin, ethereum
                        Get public companies bitcoin or ethereum holdings (Ordered by total holdings descending)

Pycoin home page: <https://github.com/PhineasPhreak/pycoin>

```

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
Used Prerequisites `pandas`, `rich`, `requests`, `openpyxl` and `pyinstaller`, `pyinstaller-versionfile`
> Documentations :
>
> pandas : [pandas pypi.org](https://pypi.org/project/pandas/) \
> rich : [rich pypi.org](https://pypi.org/project/rich/) \
> requests : [requests pypi.org](https://pypi.org/project/requests/) \
> openpyxl : [openpyxl pypi.org](https://pypi.org/project/openpyxl/) \
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
