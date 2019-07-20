FROM python:3.7
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./
RUN mkdir "_upload"
ENV UPLOAD_DIR="_upload"

WORKDIR /app/run

ENTRYPOINT [ "python" ]
CMD [ "../upload_output_files.py" ]