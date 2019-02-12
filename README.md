# My Attempt At Modernizing the PDB2PQR Server Via React and Flask

**Warning: Still under development. Homepage is up but interaction is all over the place right now.**

## Initiate Python 2 virtualenv "./venv/"
* From the repository root, run [initVenv.sh](initVenv.sh), which will build a Python 2 virtualenv at "./venv" and installs the necessary Python modules within it
```shell
./initVenv.sh
```

## To run (Python 2 virtualenv is recommended)

* Install the latest version of Flask
`pip install flask`

* From the repository root, set the appropriate environment variables for running/debug and have at it
```shell
export FLASK_APP=server.py
export FLASK_DEBUG=1
flask run
```
