# stage 1 - setup PDB2PQR binaries
FROM ubuntu:18.04

WORKDIR /app
RUN apt update -y \
    && apt install -y wget \
    && wget https://github.com/Electrostatics/apbs-pdb2pqr/releases/download/pdb2pqr-2.1.1_release/pdb2pqr-linux-bin64-2.1.1.tar.gz \
    && gunzip pdb2pqr-linux-bin64-2.1.1.tar.gz \
    && tar -xf pdb2pqr-linux-bin64-2.1.1.tar \
    && rm pdb2pqr-linux-bin64-2.1.1.tar

WORKDIR /app/run

ENTRYPOINT [ "../pdb2pqr-linux-bin64-2.1.1/pdb2pqr" ]
# ENTRYPOINT [ "python pdb2pqr.py" ]
# ENTRYPOINT [ "bash" ]