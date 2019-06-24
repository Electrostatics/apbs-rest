import sys, os
from os import environ
from flask import Flask
from flask_api import FlaskAPI
from .uid_service import uid_gen

app = FlaskAPI(__name__)
# app = Flask(__name__)
app.register_blueprint(uid_gen)

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5003'))
    except ValueError:
        PORT = 5003

    app.run(HOST, PORT)