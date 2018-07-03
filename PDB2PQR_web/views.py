from flask import render_template
from PDB2PQR_web import app

@app.route('/')
def hello_world():
    return "Hello, world!!!"