from flask import render_template
from PDB2PQR_web import app

@app.route('/')
@app.route('/home')
def home():
    return render_template("index.html")

# @app.route('pdb2pqr')
# def pdb2pqr_config():

# @app.route('/apbs')
# def apbs_config():