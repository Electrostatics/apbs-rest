import sys, os
sys.path.append(os.getcwd())

from os import environ
from flask import Flask
from flask_cors import CORS
from uid_service import uid_gen

app = Flask(__name__)
CORS(app)
app.register_blueprint(uid_gen)

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5003'))
    except ValueError:
        PORT = 5003

    app.run(HOST, PORT)