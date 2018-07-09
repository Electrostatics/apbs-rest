from flask import render_template, redirect
from PDB2PQR_web import app

navbar_links = {
    "navbar_home"     : "/home",
    "navbar_about"    : "http://www.poissonboltzmann.org/"
}

@app.route('/')
@app.route('/home')
def home():
    # return render_template("index.html", navbar_home="/", navbar_about="http://www.poissonboltzmann.org/")
    return render_template("index.html", **navbar_links)

# @app.route('/pdb2pqr')
# def pdb2pqr_config():

# @app.route('/apbs')
# def apbs_config():

@app.route('/about')
def about():
    return redirect(navbar_links["navbar_about"])