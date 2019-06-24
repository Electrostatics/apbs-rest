import sys, os
from os import environ
from flask import Flask
from flask_api import FlaskAPI
from .task_service import task_app

app = FlaskAPI(__name__)
# app = Flask(__name__)
app.register_blueprint(task_app)

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5004'))
    except ValueError:
        PORT = 5004

    app.run(HOST, PORT)