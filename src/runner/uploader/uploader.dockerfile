FROM python:3.7
WORKDIR /app
COPY . ./
RUN mkdir "_upload"
ENV UPLOAD_DIR="_upload"

WORKDIR /app/run
ENTRYPOINT [ "python ../upload_output_files.py" ]