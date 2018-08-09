from flask import Flask

'''Specifies location of static React files to deliver'''
app = Flask(
    __name__,
    static_folder="build/static",
    template_folder="build")

import PDB2PQR_web.views