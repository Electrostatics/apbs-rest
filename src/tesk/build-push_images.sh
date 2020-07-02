#!/bin/sh

set -e

if [ $1 = 'apbs' ]
then
    cd tesk_execution
    docker build -t electrostatics/apbs-bin:edge -f apbs-bin.dockerfile .
    docker push electrostatics/apbs-bin:edge
elif [ $1 = 'pdb2pqr' ]
then
    # cd tesk_execution
    # docker build -t electrostatics/pdb2pqr-tesk:latest -f pdb2pqr-tesk.dockerfile .
    # docker push electrostatics/pdb2pqr-tesk:latest

    cd tesk_execution
    cp ../../pdb2pqr_build_materials/main.py .
    docker build -t electrostatics/pdb2pqr-bin:edge -f pdb2pqr-bin-source.dockerfile .
    docker push electrostatics/pdb2pqr-bin:edge
    rm main.py
elif [ $1 = 'tesk-proxy' -o $1 = 'proxy' ]
then
    cd tesk_proxy
    docker build -t electrostatics/apbs-tesk-proxy:edge .
    docker push electrostatics/apbs-tesk-proxy:edge
fi