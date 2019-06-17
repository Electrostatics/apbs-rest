FROM python:3.7
WORKDIR /app
COPY . ./
ENV APP_RUN_DIR="/app/run"

WORKDIR /app/run
ENTRYPOINT [ "python ../download_input_files.py" ]