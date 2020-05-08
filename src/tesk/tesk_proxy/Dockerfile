# stage 1 - build APBS and PDB2PQR
FROM ubuntu:18.04 as apbs_pdb2pqr-build

WORKDIR /app
RUN apt update -y \
    && apt install -y python-pip swig g++ make git wget

RUN wget https://github.com/Kitware/CMake/releases/download/v3.16.2/cmake-3.16.2-Linux-x86_64.tar.gz \
    && gunzip cmake-3.16.2-Linux-x86_64.tar.gz \
    && tar -xf cmake-3.16.2-Linux-x86_64.tar \
    && git clone https://github.com/Electrostatics/apbs-pdb2pqr.git

WORKDIR /app/apbs-pdb2pqr/apbs
RUN git checkout b3bfeec \
    && git submodule init \
    && git submodule update \
    && mkdir -p /app/builds/apbs \
    && cd /app/builds/apbs \
    && export PATH=$PATH:/app/cmake-3.16.2-Linux-x86_64/bin \
    && cmake /app/apbs-pdb2pqr/apbs -DENABLE_PYTHON=ON -DBUILD_SHARED_LIBS=ON \
    && make
# WORKDIR /app/apbs_build
# RUN cmake /app/apbs-pdb2pqr/apbs -DENABLE_PYTHON=ON -DBUILD_SHARED_LIBS=ON \
#     && make

COPY service/legacy/build_config.py /app/apbs-pdb2pqr/pdb2pqr/build_config.py

WORKDIR /app/apbs-pdb2pqr/pdb2pqr
RUN python scons/scons.py install

WORKDIR /app
COPY requirements.txt /app
RUN python -m pip install -r requirements.txt gunicorn==19.9.0
# COPY build_config.py apbs-pdb2pqr/pdb2pqr/build_config.py

# stage 2 - config and deploy Flask app
# FROM python:2.7-alpine
# COPY --from=apbs_pdb2pqr-build /app/apbs_build ./apbs_build
# COPY --from=apbs_pdb2pqr-build /app/pdb2pqr_build ./pdb2pqr_build
# RUN cp  ./src/pdb2pqr_build_materials/main_cgi.py \
#         ./src/pdb2pqr_build_materials/querystatus.py \
#         ./src/pdb2pqr_build_materials/apbs_cgi.py ./pdb2pqr_build

COPY . /app
WORKDIR /app/service/legacy
RUN ln -s ../../builds/pdb2pqr/src \
    && ln -s ../../builds/pdb2pqr/main.pyc

WORKDIR /app
# RUN ls -la /app/legacy
# RUN export FLASK_APP=server.py
# RUN export FLASK_DEBUG=1
# ENV FLASK_APP=server.py
# ENV FLASK_DEBUG=1
ENV FLASK_RUN_HOST="0.0.0.0" \
    FLASK_RUN_PORT="5007" \
    PDB2PQR_BUILD_PATH=/app/builds/pdb2pqr

EXPOSE 5007

# ENTRYPOINT [ "flask" ]
# CMD [ "run" ]
ENTRYPOINT [ "gunicorn" ]
CMD [ "-w", "4", "-b", "0.0.0.0:5007", "main:app" ]
