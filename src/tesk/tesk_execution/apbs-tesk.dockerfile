FROM electrostatics/apbs-bin:1.5

RUN apt install -y curl


COPY upload_results.sh /app/
# WORKDIR /app/run

ENTRYPOINT [ "apbs" ]