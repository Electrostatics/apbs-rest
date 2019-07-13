import sys, os
from os import environ
from flask import Flask
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv()
from service.workflow_service import workflow_app

app = Flask(__name__)
CORS(app)
app.register_blueprint(workflow_app)

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5000'))
    except ValueError:
        PORT = 5000

    app.run(HOST, PORT)