import sys, os
from os import environ
from flask import Flask
import storage_service

app = Flask(__name__)
app.register_blueprint(storage_service.storage_app)

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5001'))
    except ValueError:
        PORT = 5001
    app.run(HOST, PORT)