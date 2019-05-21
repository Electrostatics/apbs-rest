import sys, os
from os import environ
from dotenv import load_dotenv
load_dotenv()
# Adds build directory to module path to for module compatibility
sys.path.append(os.getcwd() + "/pdb2pqr_build")
sys.path.append(os.getcwd() + "/src")

from PDB2PQR_web import app

if __name__ == '__main__':
    HOST = environ.get('FLASK_RUN_HOST', 'localhost')
    try:
        PORT = int(environ.get('FLASK_RUN_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
    # app.run('0.0.0.0', PORT)