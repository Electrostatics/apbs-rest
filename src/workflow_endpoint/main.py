import sys, os
from os import environ
from flask import Flask
from flask_api import FlaskAPI
from flask_cors import CORS
from .workflow_service import workflow_app

app = FlaskAPI(__name__)
CORS(app)
# app = Flask(__name__)
app.register_blueprint(workflow_app)

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5000'))
    except ValueError:
        PORT = 5000

    app.run(HOST, PORT)