# APBS-REST Command Line Tools

## Contents
- [Basic Usage](#basic-usage)
- [Requirements](#requirements)
- [Build](#build)

## Basic Usage
Using the command line tools should mirror the same interface as the current tools for APBS and PDB2PQR:
- APBS
    ```shell
    apbs [options] input-file
    ```
    Further details can be found in the APBS [documentation](https://apbs-pdb2pqr.readthedocs.io/en/latest/apbs/invoking.html).

- PDB2PQR
    ```shell
    pdb2pqr [options] --ff={forcefield} {pdb-path} {output-path}
    ```
    Further details can be found in the PDB2PQR [documentation](https://apbs-pdb2pqr.readthedocs.io/en/latest/pdb2pqr/invoking.html).


## Requirements
Requirements for development/building the APBS-CLI tools: 
- [Go](https://golang.org/dl/) (Golang) &ge; 1.11
    - Module support was implemented in this version

## Build
If you have a Go installer, there's no need to clone this repository.
- Get the respective packages:
    ```shell
    go get github.com/Electrostatics/apbs-rest/cli/apbs
    go get github.com/Electrostatics/apbs-rest/cli/pdb2pqr
    ```
- From your directory of choice, ```go build``` the binary you need:
    ```shell
    go build github.com/Electrostatics/apbs-rest/cli/apbs
    go build github.com/Electrostatics/apbs-rest/cli/pdb2pqr
    ```

If you have the repository cloned, ```go build``` from within your directory of choice to create the binaries:
- APBS
  ```shell
  $ go build apbs/
  ```

- PDB2PQR
  ```shell
  $ go build pdb2pqr/
  ```
