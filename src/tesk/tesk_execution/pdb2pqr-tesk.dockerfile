FROM electrostatics/pdb2pqr-bin:2.1.1

RUN apt install -y curl

COPY upload_results.sh /app/
ENV PATH="${PATH}:/app/pdb2pqr-linux-bin64-2.1.1"
# WORKDIR /app/run

ENTRYPOINT [ "pdb2pqr" ]
