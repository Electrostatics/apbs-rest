from os import environ
from flask import Flask
from flask_api import FlaskAPI
from flask_cors import CORS
from . import autofill_service

# app = Flask(__name__)
app = FlaskAPI(__name__)
CORS(app)
app.register_blueprint(autofill_service.autofill_app)

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5006'))
    except ValueError:
        PORT = 5006
    app.run(HOST, PORT)