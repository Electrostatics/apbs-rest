from flask import render_template, redirect
from PDB2PQR_web import app
import pdb2pqr.main_cgi
# import pdb2pqr.main_cgi

navbar_links = {
    "navbar_home"     : "/home",
    "navbar_about"    : "http://www.poissonboltzmann.org/",
    "legacy_ucsd"     : "http://nbcr-222.ucsd.edu/pdb2pqr_2.1.1/"
}

@app.route('/')
@app.route('/home')
def home():
    # return render_template("index.html", navbar_home="/", navbar_about="http://www.poissonboltzmann.org/")
    return render_template("index.html", **navbar_links)

@app.route('/jobstatus')
def jobstatus():
    return "Need to build this page"

# @app.route('/apbs')
# def apbs_config():

@app.route('/about')
def about():
    return redirect(navbar_links["navbar_about"])

@app.route('/legacy')
def legacy():
    return redirect(navbar_links["legacy_ucsd"])