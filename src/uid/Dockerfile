FROM python:3
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt gunicorn==19.9.0

# ENV FLASK_RUN_PORT="5003" \
#     FLASK_RUN_HOST="0.0.0.0" \
#     FLASK_DEBUG='0' \
#     FLASK_APP="main.py"

COPY . /app
EXPOSE 5003

# ENTRYPOINT [ "flask" ]
# CMD [ "run" ]
ENTRYPOINT [ "gunicorn" ]
CMD [ "-w", "4", "-b", "0.0.0.0:5003", "main:app" ]