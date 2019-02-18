import sys, os
from os import environ

# Adds build directory to module path to for module compatibility
sys.path.append(os.getcwd() + "/pdb2pqr_build")

from PDB2PQR_web import app

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)