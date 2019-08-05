# APBS-REST: Deploying APBS as a Containerized Microservice-Based Software

**Warning: Still under development. Stability not guaranteed.**  
**Tested using build of APBS-PDB2PQR through Ubuntu**

## Table of Contents
* [Preface](##Preface)
* [System Requirements](##System-Requirements)
* [Setup](##Setup)
* [Execution](##Execution)
<!-- * [Quickstart](##Quickstart) -->

## Preface
This repository serves as the backend interface for an overhauled PDB2PQR web server.  As such, the code contained herein serves as **one of three** components necessary to fully operate the website.  The frontend interface and APBS-PDB2PQR software should be cloned and built separately.  Links to both are below, respectively:
* [antd_pdb2pqr](https://github.com/Eo300/antd_pdb2pqr) (front-end)
  * After cloning to your desired location, use the ```npm run build``` command to build a production-ready version of the latest build
  * [**UPDATE**] With a recent move to Dockerize this component, building this frontend component may not be necessary as the build would exist in it's own container
* [apbs-pdb2pqr](https://github.com/Electrostatics/apbs-pdb2pqr)  
  * You will need to build APBS and PDB2PQR since both are used for the job functions of the website

For both of the above, feel free to clone them in a location of your choosing, though I did so outside of this repository to avoid confusion within Git. 

## System Requirements
### For Users
To simply run the suite as a user, the following software is required
- [Helm](https://helm.sh/) 
- A Kubernetes engine such as...
    - [Minikube (recommended)](https://kubernetes.io/docs/tasks/tools/install-minikube/)
    - [Docker Desktop (includes Kubernetes)]()
### For Developers
All of the above along with...
- [Python 3.6+](https://www.python.org/downloads/)
- [Python 2.7](https://www.python.org/downloads/release/python-2716/)
    - for development on services using legacy PDB2PQR code

<!-- ## Quickstart
### For Users -->

## Setup
### Initiate Python virtualenv "./venv/"  
From the repository root, run [initVenv.sh](initVenv.sh), which will build a Python virtualenv at "./venv" and installs the necessary Python modules within it.
```shell
./initVenv.sh
```

### Create Symbolic Link to Website Frontend Build Directory
From the [./PDB2PQR_web](PDB2PQR_web) directory:
```shell
ln -s <PATH TO FRONTEND DIRECTORY> ./build
```

### Create Symbolic Link to Your PDB2PQR Build Directory
From the repository root:
```shell
ln -s <PATH TO PDB2PQR BUILD DIRECTORY> ./pdb2pqr_build
```

### Copy edited PDB2PQR *.py files into build directory  
From the repository root, copy the related PDB2PQR files ([main_cgi.py](src/pdb2pqr_build_materials/main_cgi.py), [apbs_cgi.py](src/pdb2pqr_build_materials/apbs_cgi.py), and [querystatus.py](src/pdb2pqr_build_materials/querystatus.py)) into the build directory as they are modified to work with the Flask server
```shell
cp main_cgi.py apbs_cgi.py querystatus.py ./pdb2pqr_build/.
```  
Alternatively, you may create a symbolic link to the aforementioned files instead. **(This is recommended if editing the files as it'd remove the need to constantly copy/paste to see new changes)**

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
