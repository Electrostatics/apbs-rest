FROM python:3.7-slim
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./
RUN mkdir "_upload"
RUN chmod +x generate_final_status.sh
ENV UPLOAD_DIR="/app/_upload"

WORKDIR /app/run

ENTRYPOINT [ "python", "../upload_output_files.py" ]