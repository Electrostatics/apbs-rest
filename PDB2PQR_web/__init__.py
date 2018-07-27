from flask import Flask
app = Flask(
    __name__,
    static_folder="build/static",
    template_folder="build")

import PDB2PQR_web.views