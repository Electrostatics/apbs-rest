FROM python:2.7
WORKDIR /app
COPY . ./
RUN python -m pip install -r requirements.txt 
        # && rm .env
        # && ls -la
ENV STORAGE_HOST="http://localhost:5001" \
    STORAGE_URL="http://localhost:5001/storage" \
    FLASK_RUN_PORT="5002" \
    FLASK_RUN_HOST="0.0.0.0" \
    FLASK_DEBUG="1" \
    FLASK_APP="main.py"
RUN echo $FLASK_APP

EXPOSE 5002

ENTRYPOINT [ "python" ]
CMD [ "main.py" ]

# ENTRYPOINT [ "flask" ]
# CMD [ "run" ]