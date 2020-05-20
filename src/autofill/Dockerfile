# stage 1 - build APBS and PDB2PQR
FROM ubuntu:18.04 as apbs_pdb2pqr-build
WORKDIR /app
RUN apt update -y \
    && apt install -y python-pip swig cmake g++ make git \
    && git clone https://github.com/Electrostatics/apbs-pdb2pqr.git \
    # Checkout commit before PDB2PQR v3.0 changes
    && cd /app/apbs-pdb2pqr \
    && git checkout b3bfeec


COPY build_config.py /app/apbs-pdb2pqr/pdb2pqr/build_config.py
WORKDIR /app/apbs-pdb2pqr/pdb2pqr
RUN python scons/scons.py install

COPY requirements.txt /app
RUN cd /app && python -m pip install -r requirements.txt

# stage 2 - config and deploy Flask app
COPY . /app

WORKDIR /app/legacy
RUN ln -s ../builds/pdb2pqr/src
# COPY ../../pdb2pqr_build_materials/apbs_cgi.py .
COPY apbs_cgi.py .

WORKDIR /app
RUN rm /app/legacy/*.pyc /app/apbs_cgi.py

# ENV FLASK_APP=server.py
# ENV FLASK_DEBUG=1
ENV FLASK_RUN_HOST="0.0.0.0" \
    FLASK_RUN_PORT="5006"

EXPOSE 5006

ENTRYPOINT [ "flask" ]
CMD [ "run" ]