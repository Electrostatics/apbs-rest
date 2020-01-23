from __future__ import print_function
from flask import request, Blueprint, render_template
# from flask import url_for
import os, logging

STORAGE_URL  = os.environ.get('STORAGE_URL' , 'http://localhost:5001/api/storage')
viz_service = Blueprint('viz_service', __name__)

''' 
    Below is the endpoint to view a visualation of a protein post-APBS.
    This serves to replicate the version of the visualizer present on the
        UCSD PDB2PQR web server (http://nbcr-222.ucsd.edu/pdb2pqr_2.1.1/).
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
    # pqr_name = None
    pqr_prefix = None
    missing_args = []
    
    # Obtain jobid from querystring if exists; otherwise set error code
    if 'jobid' in request.args:
        job_id = request.args.get('jobid')
    else:
        missing_args.append('jobid')
        if http_status < 400:
            http_status = 400

    # TODO: consider whether to change 'pqr' arg to 'pqrprefix', or some variant
    if 'pqr' in request.args:
        # pqr_name = request.args.get('pqr')
        pqr_prefix = request.args.get('pqr')
    else:
        missing_args.append('pqr')
        if http_status < 400:
            http_status = 400

    if http_status == 400:
        error_message = f'Missing arguments in URL query: <b>{missing_args}</b>'
        return error_message, http_status
    else:
        # print(url_for('static', filename='3dmol/js/3dmol.js'))
        return render_template('visualize.html', jobid=job_id, pqr_prefix=pqr_prefix, storage_url=STORAGE_URL), http_status