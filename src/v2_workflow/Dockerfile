FROM python:3.7

WORKDIR /app
# COPY .env /app
COPY  requirements.txt /app
RUN pip install -r requirements.txt gunicorn==19.9.0

COPY . /app
EXPOSE 5000

# ENTRYPOINT [ "flask" ]
# CMD [ "run" ]
ENTRYPOINT [ "gunicorn" ]
CMD [ "-w", "4", "-b", "0.0.0.0:5000", "main:app" ]