#!/usr/bin/env python3

from setuptools import setup

# Load the README file.
with open(file="README.md", mode="r") as readme_handle:
    long_description = readme_handle.read()

setup(
    # Define the library name, this is what is used along with `pip install`.
    name='pycoin',

    # Define the author of the repository.
    author='Phineas Phreak',

    # Define the Author's email, so people know who to reach out to.
    # author_email='mail@example.com',

    # Define the version of this library.
    # Read this as
    #   - MAJOR VERSION 0
    #   - MINOR VERSION 1
    #   - MAINTENANCE VERSION 0
    version='1.8.6',

    # Here is a small description of the library. This appears
    # when someone searches for the library on https://pypi.org/search.
    description='Python wrapper for the CoinGecko API and argparse',

    # I have a long description but that will just be my README
    # file, note the variable up above where I read the file.
    long_description=long_description,

    # This will specify that the long description is MARKDOWN.
    long_description_content_type="text/markdown",

    # Here is the URL where you can find the code, in this case on GitHub.
    url='https://github.com/PhineasPhreak/pycoin',

    # Add the python3 module
    # scripts=['pycoin.py'],

    # Here are the packages I want "build."
    packages=['pycoin'],

    # These are the dependencies the library needs in order to run.
    install_requires=[
        'pandas',
        'rich',
        'requests',
        'openpyxl',
        'pyinstaller',
        'pyinstaller-versionfile',
    ],

    # Here are the keywords of my library.
    keywords='python3, coingecko, governments, finance, APIs, crypto',

    # I also have some package data, like photos and JSON files, so
    # I want to include those as well.
    include_package_data=True,

    # Here I can specify the python version necessary to run this library.
    python_requires='>=3.7',

)
