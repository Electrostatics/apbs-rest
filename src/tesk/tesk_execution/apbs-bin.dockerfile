# Setup APBS binaries
FROM ubuntu:18.04
WORKDIR /app
RUN apt update -y \
    && apt install -y wget libgfortran3

RUN wget https://github.com/Electrostatics/apbs-pdb2pqr/releases/download/apbs-1.5/APBS-1.5-linux64.tar.gz \
         http://mirrors.kernel.org/ubuntu/pool/main/r/readline6/libreadline6_6.3-8ubuntu2_amd64.deb

RUN apt install -y ./libreadline6_6.3-8ubuntu2_amd64.deb

RUN gunzip APBS-1.5-linux64.tar.gz \
    && tar -xf APBS-1.5-linux64.tar \
    && cd APBS-1.5-linux64/bin/

RUN rm APBS-1.5-linux64.tar

ENV LD_LIBRARY_PATH=/app/APBS-1.5-linux64/lib
ENV PATH="${PATH}:/app/APBS-1.5-linux64/bin"

WORKDIR /app/run

ENTRYPOINT [ "apbs" ]
# ENTRYPOINT [ "bash" ]