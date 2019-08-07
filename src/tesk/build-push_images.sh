#!/bin/sh

if [ $1 = 'apbs' ]
then
    cd tesk_execution
    docker build -t electrostatics/apbs-tesk:latest -f apbs-tesk.dockerfile .
    docker push electrostatics/apbs-tesk:latest
elif [ $1 = 'pdb2pqr' ]
then
    # cd tesk_execution
    # docker build -t electrostatics/pdb2pqr-tesk:latest -f pdb2pqr-tesk.dockerfile .
    # docker push electrostatics/pdb2pqr-tesk:latest

    cd tesk_execution
    cp ../../pdb2pqr_build_materials/main.py .
    docker build -t electrostatics/pdb2pqr-bin:source -f pdb2pqr-bin-source.dockerfile .
    docker push electrostatics/pdb2pqr-bin:source
    rm main.py
elif [ $1 = 'tesk-proxy' -o $1 = 'proxy' ]
then
    cd tesk_proxy
    docker build -t electrostatics/apbs-tesk-proxy:latest .
    docker push electrostatics/apbs-tesk-proxy:latest
fi