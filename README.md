# APBS-REST: Deploying APBS as a Containerized Microservice-Based Software

*This project is a work in progress. Stability not guaranteed.*

## Table of Contents
* [Overview](#overview)
    * [What is Docker?](#what-is-docker)
    * [What is Kubernetes?](#what-is-kubernetes)
<!-- * [What is Helm](#what-is-helm) -->
* [Install](#install)
    * [Prerequisites](#prerequisites)
    * [APBS-REST Installation](#apbs-rest-installation)
* [Uninstall from Cluster](#uninstall-from-cluster)
* [For Developers](#for-developers)
<!-- * [System Requirements](#system-requirements) -->
<!-- * [Setup](##Setup)
* [Execution](##Execution) -->

<hr/>

## Overview
APBS-REST serves as the beginning effort to rebuild the infrastructure powering the [APBS-PDB2PQR](https://github.com/Electrostatics/apbs-pdb2pqr) software suite.  One of the goals with the redesign is to eliminate the OS-specific idiosyncrasies/inconsistencies one must account for during development.  While the main software undergoes its own overhaul, the services herein will become a deployment mechanism by which to execute APBS or PDB2PQR.  Facilitating the development/deployment are the containerization engine [Docker](https://www.docker.com/), the container-orchestration software [Kubernetes](https://kubernetes.io/), and the Kubernetes package manager [Helm](https://helm.sh/).

### What is Docker?
<!-- From [Docker](https://www.docker.com/get-started): -->
From [Docker](https://www.docker.com/why-docker):
>Docker containers wrap up software and its dependencies into a standardized unit for software development that includes everything it needs to run: code, runtime, system tools and libraries.

An easy way to understand containers are as lightweight, ephemeral virtual machines, while Docker is the engine which powers them.  As such, it allows for isolated, consistent execution across operating systems without dealing with the variances of any individual's environment.

### What is Kubernetes?
Since the main components of APBS-REST are containerized elements, Kubernetes is utilized to serve as the orchestrator glueing each service together. From [Kubernetes.io](https://kubernetes.io/):
>Kubernetes (K8s) is an open-source system for automating deployment, scaling, and management of containerized applications.
It groups containers that make up an application into logical units for easy management and discovery.

Depending on your platform, there exist a couple installation methods: **Minikube** or **Docker Desktop** 

<!-- ### What is Minikube? -->


<!-- ## System Requirements -->
<!-- ## Prerequisites
### Users
To run the suite as a user, the following software must be installed/activated:
- [Helm](https://helm.sh/) 
- A Kubernetes engine such as...
    - [Minikube (recommended for Linux users, available on Windows)](https://kubernetes.io/docs/tasks/tools/install-minikube/)
    - [Docker Desktop (includes Kubernetes)](https://www.docker.com/products/docker-desktop)<br/>
    *Windows 10 Users: Docker Desktop uses Hyper-V for virtualization. This is only available for users of Windows 10 Pro or above (Enterprise, Education, etc.)*

**Additional guidance for potential roadblocks coming soon.**<br/><br/>
    
### Developers
All of the above along with...
- [Python 3.6+](https://www.python.org/downloads/)
- [Python 2.7](https://www.python.org/downloads/release/python-2716/)
    - for development on services using legacy PDB2PQR code
- [Docker](https://docs.docker.com/install/)
    - Certain tests require this as they utilize the [Docker SDK for Python](https://docker-py.readthedocs.io/en/stable/) -->


<!-- <br> -->
<!-- <hr> -->

## Install
### Prerequisites

Before installing APBS-REST, the following must be installed on your device:
- [Helm](https://github.com/helm/helm/releases)
- [Minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/)
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads) (required for Minikube)

The commands ```kubectl``` and ```helm``` should how be available. Verify your Minikube and Helm installations:
```
$ kubectl version
Client Version: version.Info{Major:"1", Minor:"16", GitVersion:"v1.16.2", GitCommit:"c97fe5036ef3df2967d086711e6c0c405941e14b", GitTreeState:"clean", BuildDate:"2019-10-15T19:18:23Z", GoVersion:"go1.12.10", Compiler:"gc", Platform:"darwin/amd64"}
Server Version: version.Info{Major:"1", Minor:"16", GitVersion:"v1.16.0", GitCommit:"2bd9643cee5b3b3a5ecbd3af49d09018f0773c77", GitTreeState:"clean", BuildDate:"2019-09-18T14:27:17Z", GoVersion:"go1.12.9", Compiler:"gc", Platform:"linux/amd64"}

$ helm version
Client: &version.Version{SemVer:"v2.15.2", GitCommit:"8dce272473e5f2a7bf58ce79bb5c3691db54c96b", GitTreeState:"clean"}
Server: &version.Version{SemVer:"v2.15.2", GitCommit:"8dce272473e5f2a7bf58ce79bb5c3691db54c96b", GitTreeState:"clean"}
```

**Note for Docker Desktop users:** If you already use the latest versions of Docker Desktop for Windows/Mac, Kubernetes is bundled and ready to be enabled via the Settings menu.  However, Docker Desktop for Windows requires Hyper-V, which users not on Windows 10 Professional or higher cannot access.  This is why we target Minikube for user installation of APBS-REST, as VirtualBox is available to anyone with a virtualization-compatible processor (most Intel/AMD CPUs over the past decade should have this feature).

Please note that the Kubernetes version bundled with Docker Desktop **generally lags behind (1.14.7 compared to current 1.16.2 as of this writing)** and may exhibit potential incompatibilities in the future.  If you do plan to use Docker Desktop with it's Kubernetes, the current version (v2.1.0.4) has proven compatible during development thus far.

#### Known installation issues/incompatibilities:
- Helm versions < 2.15 will will not install with Kubernetes v1.16
- During initial testing, issues were encountered when attempting to start Minikube with Hyper-V as the driver.  Your mileage may vary, but VirtualBox has yet to exhibit any issues while launching Minikube (fingers crossed).

Any additional issues discovered will be noted here.

<br>
<!-- <hr> -->

### APBS-REST Installation
#### From the top of the repository
If you've never used Helm or don't have its Tiller installed on your cluster, do the following:
```shell
kubectl create serviceaccount tiller --namespace kube-system
kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
helm init --service-account=tiller --wait
```
<br>

Enable an ingress controller for your Minikube cluster. 
```shell
minikube addons enable ingress
```
- **Docker Desktop:** ```helm install``` an NGINX ingress controller since you don't have access to Minikube. Be mindful that the ```nginx-ingress``` **consumes the localhost ports 80 and 443.**
    ```shell
    helm install -n nginx-ingress --namespace kube-system stable/nginx-ingress
    ```
An ingress object manages/defines how external network access to services within the cluster is routed, and the ingress controller does the work of routing the traffic.

<br>

Finally, ```helm install``` APBS-REST onto your cluster:
```shell
helm install charts/apbs-rest -n apbs-rest --set ingress.enabled=true,ingress.hosts[0]=apbs.$(minikube ip).xip.io
```
- **Docker Desktop:** this step differs in that you'd use the localhost IP address.
    ```shell
    helm install charts/apbs-rest -n apbs-rest --set ingress.enabled=true,ingress.hosts[0]=apbs.127.0.0.1.xip.io
    ```
The cluster will begin downloading the necessary images and readying the application.  Walk away and grab a coffee, because this step can take upwards of ~6 minutes (+/- based on your network speeds).  Review the arguments via ```helm install --help``` if you wish to understand the flags used above.

If you'd like to view the installation status, execute the following:
```shell
helm status apbs-rest
```
The output here will look familiar as it's the output from the previous install command. Specifically, seek out the section labeled ```v1/Deployment```
```
==> v1/Deployment
NAME                  READY  UP-TO-DATE  AVAILABLE  AGE
apbs-rest-autofill    1/1    1           1          10m
apbs-rest-id          1/1    1           1          10m
apbs-rest-minio       1/1    1           1          10m
apbs-rest-storage     1/1    1           1          10m
apbs-rest-task        1/1    1           1          10m
apbs-rest-tesk        1/1    1           1          10m
apbs-rest-tesk-proxy  1/1    1           1          10m
apbs-rest-ui          1/1    1           1          10m
apbs-rest-workflow    1/1    1           1          10m
```
When you see that all deployments are in the READY state, you're good to go.  Find the host via the "Ingress" header of the ```helm status apbs-rest``` output. Use your browser to navigate to there and enjoy!

#### Uninstall
There's more regarding the uninstalling process [below](#uninstall-from-cluster), but it ultimately is just a ```helm delete``` on the name of the application (indicated by ```-n``` flag in the previous installation command)
```shell
helm delete --purge apbs-rest
```


#### All commands for easy Copy+Paste
- Minikube
    ```shell
    kubectl create serviceaccount tiller --namespace kube-system
    kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller

    helm init --service-account=tiller --wait
    minikube addons enable ingress
    helm install charts/apbs-rest -n apbs-rest --set ingress.enabled=true,ingress.hosts[0]=apbs.$(minikube ip).xip.io
    ```
- Docker Desktop
    ```shell
    kubectl create serviceaccount tiller --namespace kube-system
    kubectl create clusterrolebinding tiller-cluster-rule --clusterrole=cluster-admin --serviceaccount=kube-system:tiller
    
    helm init --service-account=tiller --wait
    helm install -n nginx-ingress --namespace kube-system stable/nginx-ingress
    helm install charts/apbs-rest -n apbs-rest --set ingress.enabled=true,ingress.hosts[0]=apbs.127.0.0.1.xip.io
    ```


<hr/>

## Uninstall from Cluster
To uninstall the APBS-REST software from your local kubernetes cluster, simply type the following:
```
helm delete --purge apbs-rest
```
This will remove the release from your cluster **along with any associated storage volumes.  Make certain you download any output files you need from the cluster before removing APBS-REST from your local cluster.**

<hr/>

## For Developers

### Preface
This repository serves as the backend interface for an overhauled APBS web server.  As such, the code contained herein serves as **one of two** components necessary to develop on the website:
* [apbs-web](https://github.com/Eo300/apbs-web) (front-end)
  * After cloning to your desired location, use the ```npm run dev``` command to run a development server with the defined environment variables.
  * [**UPDATE**] With the move to Dockerize this component, building this frontend component is no longer needed as the build exists in it's own container
* [apbs-pdb2pqr](https://github.com/Electrostatics/apbs-pdb2pqr)  
  * You will need to build APBS and PDB2PQR depending on which service you plan to develop for, as some use the legacy code via symlinks

For both of the above, feel free to clone them in a location of your choosing, though it's recommended to be done outside of this repository to avoid confusion with Git checking for file changes.

### Microservices

All the microservices live within the src directory. A list of all the services used within the Helm chart are as follows:
- [autofill](src/autofill)<sup>1</sup>
- [storage](src/storage)
- [task](src/task)
- [tesk-proxy](src/tesk)
- [uid](src/uid)
- [workflow](src/v2_workflow)

<sup>1</sup> Some services are dependent on legacy code from the original apbs-pdb2pqr repository.  Thus, you'd need to have a APBS/PDB2PQR build somewhere on your system and specific paths symlinked to the respective service.
<!-- Details are available within the respective README files per service. -->

