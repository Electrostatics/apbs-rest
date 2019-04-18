from flask import render_template, redirect, request, send_from_directory, make_response
from werkzeug import secure_filename
from json import JSONEncoder
from PDB2PQR_web import app
from PDB2PQR_web import jobutils
from src.aconf import *
from src import inputgen
from src import psize
import os
import main_cgi # main driver for PDB2PQR
import querystatus
# import pdb2pqr.main_cgi
import apbs_cgi # main driver for APBS
import time

navbar_links = {
    "navbar_home"     : "/home",
    "navbar_about"    : "http://www.poissonboltzmann.org/",
    "legacy_ucsd"     : "http://nbcr-222.ucsd.edu/pdb2pqr_2.1.1/"
}

ORIGIN_WHITELIST = [
    'http://localhost:3000/jobstatus',
    'http://localhost:8000/jobstatus',
    'http://localhost:3000/apbs',
    'http://localhost:8000/apbs',
]

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
        # f = request.files['PDB']
        # print("f is of type: "+str(type(f)))
        # print(f['PDB'])
        # filename = secure_filename(f.filename)
        # print('filename: ' + filename)
        job_type = request.args['submitType']
        # print(job_type)
        # print(request.args)
        if job_type == 'pdb2pqr':
            redirectURL = main_cgi.mainCGI(request.form, request.files)
        elif job_type == 'apbs':
            import pprint as pp
            print(pp.pformat(request.form.to_dict(), indent=4, width=10))
            # return pp.pformat(request.form.to_dict(), indent=4, width=10)

            # return str(request.form)
            # return str(request.form['removewater'])
            redirectURL = apbs_cgi.mainInput(request.form)
            pass

        return redirect(redirectURL)

    elif request.method == 'GET':
        return render_template( "index.html")


@app.route('/about', methods=['GET'])
def about():
    """Currently redirects to http://www.poissonboltzmann.org/"""
    return redirect(navbar_links["navbar_about"])


@app.route('/legacy', methods=['GET'])
def legacy():
    """Redirects to the old PDB2PQR web server at http://nbcr-222.ucsd.edu/pdb2pqr_2.1.1/"""
    return redirect(navbar_links["legacy_ucsd"])


@app.route('/api/jobstatus', methods=['GET'])
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

    json_status = {}
    if request.args.has_key('jobid'):
        '''Builds JSON response if the jobid is specified in query'''
        jobid = request.args['jobid']
        # has_pdb2pqr = True # (request.args.has_key('pdb2pqr')) # ? bool(request.args['pdb2pqr']) : False
        # has_apbs = True # (request.args.has_key('apbs')) # ? bool(request.args['apbs']) : False
        has_pdb2pqr = True if ( request.args.has_key('pdb2pqr') and request.args['pdb2pqr'].lower() == 'true') else False
        has_apbs =    True if ( request.args.has_key('apbs')    and request.args['apbs'].lower() == 'true'   ) else False

        # Obtains status info for PDB2PQR
        pdb2pqr_progress = []
        pdb2pqr_status = None
        pdb2pqr_starttime = None
        pdb2pqr_endtime = None

        pdb2pqr_starttime = jobutils.get_starttime(jobid, 'pdb2pqr')
        pdb2pqr_endtime = jobutils.get_endtime(jobid, 'pdb2pqr')
        pdb2pqr_status, pdb2pqr_progress = jobutils.get_jobstatusinfo(jobid, 'pdb2pqr')

        # Obtains status info for APBS
        apbs_progress = []
        apbs_status = None
        apbs_starttime = None
        apbs_endtime = None
        
        apbs_starttime = jobutils.get_starttime(jobid, 'apbs')
        apbs_endtime = jobutils.get_endtime(jobid, 'apbs')
        apbs_status, apbs_progress = jobutils.get_jobstatusinfo(jobid, 'apbs')

        # Builds JSON response of job status
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
    # origin_whitelist = ['http://localhost:3000/jobstatus', 'http://localhost:8000/jobstatus']
    request_origin_url = request.referrer.split('?')[0]

    ''' Prepare response to API request '''
    response = make_response(JSONEncoder().encode(json_status))
    # response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    if request_origin_url in ORIGIN_WHITELIST:
        cleared_domain = request_origin_url[:request_origin_url.index('/jobstatus')]
        response.headers['Access-Control-Allow-Origin'] = cleared_domain

    # response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    
    # return JSONEncoder().encode(json_status)
    return response

@app.route('/api/autofill/jobs/<job_type>/<job_id>', methods=['GET'])
def autofill(job_id, job_type):
    json_response_dict = {}
    json_response_dict['dummy'] = 'fetch succeeded'
    # print('job_id:   '+job_id)
    # print('job_type: '+job_type)

    if job_type == 'apbs' and job_id:
        json_response_dict = apbs_cgi.unpickleVars(job_id)
        # print(type(json_response_dict))
        # print(type(json_response_dict['dime']))
        # print(len(json_response_dict.keys()))

    ''' Prepare response to API request '''
    response = make_response(JSONEncoder().encode(json_response_dict))
    request_origin_url = request.referrer.split('?')[0]
    if request_origin_url in ORIGIN_WHITELIST:
        cleared_domain = request_origin_url[:request_origin_url.index('/apbs')]
        response.headers['Access-Control-Allow-Origin'] = cleared_domain

    return response

def allowed_file(filename, valid_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in valid_extensions

# @app.route('/upload', methods=['GET', 'POST'])
@app.route('/api/upload/autofill/pqr', methods=['POST', 'OPTIONS'])
def upload_autofill():
    print("helloooo")
    EXTENSION_WHITELIST = set(['pqr'])
    json_response = None
    http_status_response = None
    app.config['UPLOAD FOLDER'] = os.path.join(INSTALLDIR, TMPDIR)

    if request.method == 'POST':
        # print(dict(request.files).keys())
        print(request)
        try:
            print(request.files.keys())
            files = request.files['file']
            if files:
                filename = secure_filename(files.filename)
                # filename = 
                mime_type = files.content_type

                if files and allowed_file(files.filename, EXTENSION_WHITELIST):
                    print("passed whitelist")
                    new_job_id = str(time.time()).replace('.' , '')
                    tmp_dir_path = os.path.join(INSTALLDIR, TMPDIR)
                    job_dir_path = os.path.join(tmp_dir_path, new_job_id)
                    upload_path  = os.path.join(job_dir_path, '%s.pqr' % (new_job_id) )
                    if not os.path.exists(job_dir_path):
                        print("passed does_exists()")
                        os.makedirs(job_dir_path)
                        files.save(upload_path)

                        # Lifted from main_cgi.py APBS handler, line 626
                        method = "mg-auto"
                        size = psize.Psize()
                        size.parseInput(upload_path)
                        size.runPsize(upload_path)
                        async = 0 # No async files here!
                        myinput = inputgen.Input(upload_path, size, method, async, potdx=True)
                        myinput.printInputFiles()
                        myinput.dumpPickle()
                        # return autofill(new_job_id, 'apbs')
                        json_response = {
                            'upload_status': 'Success',
                            'job_id': new_job_id,
                        }
                        http_status_response = 201

                        # json_response = apbs_cgi.unpickleVars(new_job_id)
                else:
                    raise Exception('File must be a PQR file')

        except Exception as e:
            # json_response = 'failed: %s' % (e)
            json_response = '%s' % (e)
            http_status_response = 500

    ''' Prepare response to API request '''
    response = make_response(JSONEncoder().encode(json_response))
    if request.method == 'OPTIONS':
        # json_response = 'this is OPTIONS'
        print('this is OPTIONS')
        response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        http_status_response = 204
    if request.referrer:
        # Add origin header to response if origin is in whitelist
        request_origin_url = request.referrer.split('?')[0]
        if request_origin_url in ORIGIN_WHITELIST:
            print(request_origin_url)
            cleared_domain = request_origin_url[:request_origin_url.index('/apbs')]
            response.headers['Access-Control-Allow-Origin'] = cleared_domain

    return response, http_status_response

    # if request.method == 'GET':
    #     pass
        
    # pass


@app.route('/download/<job_id>/<file_name>')
def job_file(job_id, file_name):
    """Delivers files from temporary directory for the appropriate job"""
    job_path = os.path.join(INSTALLDIR, TMPDIR, job_id)
    return send_from_directory(job_path, file_name)