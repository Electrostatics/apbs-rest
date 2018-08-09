from flask import render_template, redirect, request, send_from_directory, make_response
from PDB2PQR_web import app
from PDB2PQR_web import jobutils
import os
import main_cgi
import querystatus
# import pdb2pqr.main_cgi

navbar_links = {
    "navbar_home"     : "/home",
    "navbar_about"    : "http://www.poissonboltzmann.org/",
    "legacy_ucsd"     : "http://nbcr-222.ucsd.edu/pdb2pqr_2.1.1/"
}

@app.route('/', methods=["GET", "POST"])
@app.route('/home', methods=["GET", "POST"])
@app.route('/pdb2pqr', methods=["GET", "POST"])
@app.route('/apbs', methods=["GET", "POST"])
def home():
    """Delivers website to user
    
    All the above route here because the content shown is determined by React Router
    """
    return render_template("index.html")


@app.route('/jobstatus', methods=["GET", "POST"])
def jobstatus():
    """
    Handles job requests depending on method

    POST handles job submission/startup, redirecting user to the status page
    GET takes the user directly to the status page

    A query string in the URL is how the status page is rendered
    """
    if request.method == 'POST':
        f = request.files
        redirectURL = main_cgi.mainCGI(request.form, request.files)
        return redirect(redirectURL)

    elif request.method == 'GET':
        return render_template( "index.html")


@app.route('/about')
def about():
    """Currently redirects to http://www.poissonboltzmann.org/"""
    return redirect(navbar_links["navbar_about"])


@app.route('/legacy')
def legacy():
    """Redirects to the old PDB2PQR web server at http://nbcr-222.ucsd.edu/pdb2pqr_2.1.1/"""
    return redirect(navbar_links["legacy_ucsd"])


@app.route('/api/jobstatus')
def status_and_files():
    """API interface for fetching job status
    
    Given a query string containing 'jobid' with a valid ID, a JSON response is constructed with the status of the specicied job.
    Query string must specify which job type is desired.  In other words, the responses are assumed false unless specified otherwise.

    With a query string of '?jobid=15336614662&pdb2pqr=true&apbs=true', Flask should return:
        {
            "apbs": {
                "status": null,
                "files": [],
                "endTime": null,
                "startTime": null
            },
            "pdb2pqr": {
                "status": "complete",
                "files": ["http://localhost:5000/tmp/15336614662/15336614662-input.p", "http://localhost:5000/tmp/15336614662/15336614662.in", "http://localhost:5000/tmp/15336614662/15336614662.pdb", "http://localhost:5000/tmp/15336614662/15336614662.pqr", "http://localhost:5000/tmp/15336614662/15336614662.summary"],
                "endTime": 1533661467.76,
                "startTime": 1533661466.62
            },
            "jobid": "15336614662"
        }

    """
    from src.aconf import *
    from json import JSONEncoder

    json_status = {}
    if request.args.has_key('jobid'):
        '''Builds JSON response if the jobid is specified in query'''
        jobid = request.args['jobid']
        # has_pdb2pqr = True # (request.args.has_key('pdb2pqr')) # ? bool(request.args['pdb2pqr']) : False
        # has_apbs = True # (request.args.has_key('apbs')) # ? bool(request.args['apbs']) : False
        has_pdb2pqr = True if ( request.args.has_key('pdb2pqr') and request.args['pdb2pqr'].lower() == 'true') else False
        has_apbs =    True if ( request.args.has_key('apbs')    and request.args['apbs'].lower() == 'true'   ) else False

        ''' Obtains status info for PDB2PQR '''
        pdb2pqr_progress = []
        pdb2pqr_status = None
        pdb2pqr_starttime = None
        pdb2pqr_endtime = None

        pdb2pqr_starttime = jobutils.get_starttime(jobid, 'pdb2pqr')
        pdb2pqr_endtime = jobutils.get_endtime(jobid, 'pdb2pqr')
        pdb2pqr_status, pdb2pqr_progress = jobutils.get_jobstatusinfo(jobid, 'pdb2pqr')

        ''' Obtains status info for APBS '''
        apbs_progress = []
        apbs_status = None
        apbs_starttime = None
        apbs_endtime = None
        
        apbs_starttime = jobutils.get_starttime(jobid, 'apbs')
        apbs_endtime = jobutils.get_endtime(jobid, 'apbs')
        apbs_status, apbs_progress = jobutils.get_jobstatusinfo(jobid, 'apbs')

        ''' Builds JSON response of job status '''
        json_status['jobid'] = jobid
        if has_pdb2pqr:
            json_status['pdb2pqr'] = {
                'status': pdb2pqr_status,
                'files': pdb2pqr_progress[1:],
                'startTime': pdb2pqr_starttime,
                'endTime': pdb2pqr_endtime
            }
        if has_apbs:
            json_status['apbs'] = {
                'status': apbs_status,
                'files': apbs_progress[1:],
                'startTime': apbs_starttime,
                'endTime': apbs_endtime
            }

        # return JSONEncoder().encode(json_status)

    else:
        '''Returns jobid as null if jobid not specified in query'''
        json_status['jobid'] = None

    ''' FOR TESTING: allows React dev environment to fetch from here '''
    response = make_response(JSONEncoder().encode(json_status))
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    
    # return JSONEncoder().encode(json_status)
    return response

@app.route('/tmp/<jobid>/<filename>')
def job_file(jobid, filename):
    """Delivers files from temporary directory for the appropriate job"""
    from src.aconf import *
    job_path = os.path.join(INSTALLDIR, TMPDIR, jobid)
    return send_from_directory(job_path, filename)