# My Attempt At Modernizing the PDB2PQR Server Via React and Flask

**Warning: Still under development. Homepage is up but interaction is all over the place right now.**  
**Tested using build of APBS-PDB2PQR through Ubuntu**

## Table of Contents
* [Preface](##Preface)
* [Setup](##Setup)
* [Execution](##Execution)

## Preface
This repository servers as the backend interface for an overhauled PDB2PQR web server.  As such, the code contained herein serves as **one of three** components necessary to fully operate the website.  The frontend interface and APBS-PDB2PQR software should be cloned and built separately.  Links to both are below, respectively:
* [antd_pdb2pqr](https://github.com/Eo300/antd_pdb2pqr) (front-end)
  * After cloning to your desired location, use the ```npm run build``` command to build a production-ready version of the latest build
* [apbs-pdb2pqr](https://github.com/Electrostatics/apbs-pdb2pqr)  

For both of the above, feel free to clone them in a location of your choosing, though I did so outside of this repository to avoid confusion within Git. 

## Setup
### Initiate Python virtualenv "./venv/"  
From the repository root, run [initVenv.sh](initVenv.sh), which will build a Python virtualenv at "./venv" and installs the necessary Python modules within it.
```shell
./initVenv.sh
```

### Create Symbolic Link to Website Frontend Build Directory
```shell
ln -s <PATH TO FRONTEND DIRECTORY> ./build
```

### Create Symbolic Link to Your PDB2PQR Build Directory
```shell
ln -s <PATH TO PDB2PQR BUILD DIRECTORY> ./pdb2pqr_build
```

### Copy edited PDB2PQR *.py files into build directory  
From the repository root, copy related PDB2PQR files ([main_cgi.py](main_cgi.py), [pdb2pqr.py](pdb2pqr.py), and [querystatus.py](querystatus.py)) into the build directory as they are modified to work with the Flask server
```shell
cp main_cgi.py pdb2pqr.py querystatus.py ./pdb2pqr_build/.
```  
Alternatively, you may create a symbolic link to the aforementioned files instead

## Execution
### To run the Flask server (Python virtualenv is recommended)
* Usage of a Python virtual environment is recommended (see "Initiate Python virtualenv './venv/'" above)

* Install the latest version of Flask (should already be installed if [initVenv.sh](initVenv.sh) was run)

* From the **repository root**, set the appropriate environment variables for running/debug and have at it
```shell
export FLASK_APP=server.py
export FLASK_DEBUG=1
flask run
```
