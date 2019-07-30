FROM python:3.7-alpine
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./
ENV APP_RUN_DIR="/app/run"

WORKDIR /app/run
ENTRYPOINT [ "python" , "../download_input_files.py" ]