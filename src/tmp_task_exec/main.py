import sys, os
from os import environ
# sys.path.append(os.getcwd())
from flask import Flask
from flask_api import FlaskAPI
from .task_executor import tmp_executor

# sys.path.append('/' + os.path.join(*os.getcwd().split('/')[:-2]) + "/pdb2pqr_build")
PDB2PQR_BUILD_DIR = os.getenv('PDB2PQR_BUILD_DIR')

sys.path.append(PDB2PQR_BUILD_DIR)

app = FlaskAPI(__name__)
# app = Flask(__name__)
app.register_blueprint(tmp_executor)

if __name__ == "__main__":
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5005'))
    except ValueError:
        PORT = 5005

    app.run(HOST, PORT)