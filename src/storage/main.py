import sys, os
from os import environ
from flask import Flask
from flask_cors import CORS
from service import storage_service

app = Flask(__name__)
CORS(app)
app.register_blueprint(storage_service.storage_app)

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5001'))
    except ValueError:
        PORT = 5001
    app.run(HOST, PORT)