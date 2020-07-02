# Setup APBS binaries
FROM ubuntu:18.04
WORKDIR /app
RUN apt update -y \
    && apt install -y wget zip libreadline7 libgomp1

RUN wget https://github.com/Electrostatics/apbs-pdb2pqr/releases/download/vAPBS-3.0.0/APBS-3.0.0_Linux.zip \
    && unzip APBS-3.0.0_Linux.zip \
    && rm APBS-3.0.0_Linux.zip \
    && rm -r APBS-3.0.0.Linux/share/apbs/examples

ENV LD_LIBRARY_PATH=/app/APBS-3.0.0.Linux/lib
ENV PATH="${PATH}:/app/APBS-3.0.0.Linux/bin"

WORKDIR /app/run

ENTRYPOINT [ "apbs" ]