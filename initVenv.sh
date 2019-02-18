#!/bin/bash

# Initiates a Python virtal environment and installs the
# required Python modules from requirements.txt

if [ ! -d "./venv" ]; then
  python -m virtualenv venv
fi

source ./venv/bin/activate || source ./venv/Scripts/activate
pip install -r requirements.txt
