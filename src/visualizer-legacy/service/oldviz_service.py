from __future__ import print_function
from flask import request, Blueprint, render_template
# from flask import url_for
from uuid import uuid4
import os, logging, requests

STORAGE_URL  = os.environ.get('STORAGE_URL' , 'http://localhost:5001/api/storage')
GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', None)
if GA_TRACKING_ID == '': GA_TRACKING_ID = None

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

    ga_tag_js = ''
    if GA_TRACKING_ID is not None:
        if 'X-APBS-Client-ID' in request.headers:
            cid = request.headers['X-APBS-Client-ID']
        else:
            cid = str( uuid4() )

        e_category = 'apbs'
        e_action = 'visualize'
        e_label = request.headers['X-Forwarded-For']
        ga_user_agent_header = {'User-Agent': request.headers['User-Agent']}
        ga_request_body = 'v=1&tid=%s&cid=%s&t=event&ec=%s&ea=%s&el=%s\n' % (GA_TRACKING_ID, cid, e_category, e_action, e_label)

        # logging.info('Submitting analytics request - category: %s, action: %s', e_category, e_action)
        # ga_resp = requests.post('https://www.google-analytics.com/collect', data=ga_request_body, headers=ga_user_agent_header)
        # if not ga_resp.ok:
        #     ga_resp.raise_for_status

        ga_tag_js = """ <!-- Global site tag (gtag.js) - Google Analytics -->
                        <script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
                        <script>
                        window.dataLayer = window.dataLayer || [];
                        function gtag(){dataLayer.push(arguments);}
                        gtag('js', new Date());

                        gtag('config', '%s');
                        gtag('event', '%s', {
                            'event_category': '%s',
                            'event_label': '%s',
                        });
                        </script>
                    """ % (GA_TRACKING_ID, GA_TRACKING_ID, e_action, e_category, e_label)

    if http_status == 400:
        error_message = f'Missing arguments in URL query: <b>{missing_args}</b>'
        return error_message, http_status
    else:
        # print(url_for('static', filename='3dmol/js/3dmol.js'))
        return render_template('visualize.html', jobid=job_id, pqr_prefix=pqr_prefix, storage_url=STORAGE_URL, ga_tracking_tag=ga_tag_js), http_status