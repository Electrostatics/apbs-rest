# stage 1 - setup PDB2PQR binaries
FROM ubuntu:18.04

WORKDIR /app
RUN apt update -y \
    # && apt install -y wget \
    # && wget https://github.com/Electrostatics/apbs-pdb2pqr/releases/download/pdb2pqr-2.1.1_release/pdb2pqr-linux-bin64-2.1.1.tar.gz \
    # && gunzip pdb2pqr-linux-bin64-2.1.1.tar.gz \
    # && tar -xf pdb2pqr-linux-bin64-2.1.1.tar \
    # download/clone necessary files
    && apt install -y python-pip g++ make git \
    && pip install numpy

COPY main.py .
COPY build_config.py .

RUN git clone https://github.com/Electrostatics/apbs-pdb2pqr.git \
    # move custom files into repo; install PDB2PQR
    && mv main.py build_config.py /app/apbs-pdb2pqr/pdb2pqr/. \
    && cd /app/apbs-pdb2pqr/pdb2pqr \
    && python scons/scons.py \
    && python scons/scons.py install \
    && mkdir /app/run \
    && cd /app/run \
    # cleanup
    # && rm pdb2pqr-linux-bin64-2.1.1.tar \
    && rm -r /app/apbs-pdb2pqr \
    && apt autoremove -y \
    && apt clean -y \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/run

ENTRYPOINT [ "/app/builds/pdb2pqr/pdb2pqr.py" ]
# ENTRYPOINT [ "python pdb2pqr.py" ]
# ENTRYPOINT [ "bash" ]