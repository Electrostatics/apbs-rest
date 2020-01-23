from __future__ import print_function
from flask import request, Blueprint, render_template
# import uuid
from pprint import pformat
from random import choices
from string import ascii_lowercase, digits
import uuid, logging
import os

STORAGE_URL  = os.environ.get('STORAGE_URL' , 'http://localhost:5001/api/storage')
viz_service = Blueprint('viz_service', __name__)

''' 
    Below is the endpoint to generate a unique job ID string.
    This would be used to provide a client with an ID with which
        to start a workflow job.
'''

@viz_service.route('/', methods=['GET'])
@viz_service.route('/check/', methods=['GET'])
def liveness():
    """Probes server to check if alive"""
    return '', 200

@viz_service.route('/viz/3dmol', methods=['GET'])
def render_3dmol():
    http_status = 200
    job_id = None
    pqr_name = None
    missing_args = []
    # print('file' in request.args)
    # print('jobid' in request.args)
    
    # Obtain jobid from querystring if exists; otherwise set error code
    if 'jobid' in request.args:
        job_id = request.args.get('jobid')
    else:
        missing_args.append('jobid')
        if http_status < 400:
            http_status = 400

    if 'pqr' in request.args:
        pqr_name = request.args.get('pqr')
    else:
        missing_args.append('pqr')
        # TODO: uncomment below after deciding how we want user to specify the PQR prefix
        # if http_status < 400:
        #     http_status = 400

    if http_status == 400:
        error_message = f'Missing arguments in URL query: <b>{missing_args}</b>'
        return error_message, http_status
    else:
        return render_template('visualize.html', jobid=job_id, storage_url=STORAGE_URL), http_status