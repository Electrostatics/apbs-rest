FROM python:2.7-alpine
WORKDIR /app
COPY . ./
RUN python -m pip install -r requirements.txt 
        # && rm .env
        # && ls -la
ENV STORAGE_CACHE_DIR="/app/.minio_cache" \
    MINIO_URL="localhost:9000" \
    MINIO_ACCESS_KEY="xxx" \
    MINIO_SECRET_KEY="yyyyyyyy" \
    MINIO_JOB_BUCKET="jobs" \
    FLASK_RUN_PORT="5001" \
    FLASK_RUN_HOST="0.0.0.0" \
    FLASK_DEBUG="1" \
    FLASK_APP="main.py"
RUN echo $FLASK_APP

EXPOSE 5001

# ENTRYPOINT [ "python" ]
# CMD [ "main.py" ]

ENTRYPOINT [ "flask" ]
CMD [ "run" ]