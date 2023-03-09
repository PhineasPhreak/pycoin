#!/bin/bash
#
# PhineasPhreak (AS PSPK)
# Github : https://github.com/PhineasPhreak/binance-view
#

# Treat unset variables as an error
set -o nounset

env="env"
requirements="requirements.txt"


# Check if a directory exists
if [ -d "$env" ]; then
    echo "[*] Directory '$env' exist"
    exit 1;
else
    # Create virtual environment with python3 and pip
    echo "[+] Create virtual environment..."
    python3 -m venv "$env" || \
        echo "Error during the creation of the virtual environment" || exit 1;
fi
sleep 1;


# Make 'env' my environment
echo "[+] Choose '$env' like environment"
source "$env"/bin/activate || \
    echo "Error with the 'source' command" || exit 1;
echo Virtual Environment : "$VIRTUAL_ENV"
sleep 1;


# Install Python packages with pip and requirements.txt
echo "[+] Install packages with pip3"
pip3 install -r "$requirements" || \
    echo "Error during package installation with pip and 'requirements.txt' file" || exit 1;
sleep 1;
