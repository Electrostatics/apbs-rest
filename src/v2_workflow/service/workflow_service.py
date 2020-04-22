from flask import request, Blueprint
from os import getenv
from sys import stderr
from requests import get, post
from . import workflow_utils
import logging, traceback

workflow_app = Blueprint('workflow_app', __name__)
workflow_handler = workflow_utils.WorkflowHandler()

ACCEPTED_WORKFLOWS = {'apbs', 'pdb2pqr'}
END_STATES = ['complete', 'error', None]
TASK_HOST = getenv('TASK_HOST')
GA_TRACKING_ID = getenv('GA_TRACKING_ID', None)
if GA_TRACKING_ID == '': GA_TRACKING_ID = None

@workflow_app.route('/', methods=['GET'])
@workflow_app.route('/check', methods=['GET'])
def is_alive():
    return '', 200

"""
@workflow_app.route('/api/workflow/ip/', methods=['GET'])
def dummy_path():
    response = {}
    logging.info('remote_addr: %s', request.remote_addr)
    # response['remote_addr'] = request.remote_addr

    if 'X-Forwarded-For' in request.headers:
        logging.info('X-Forwarded-For: %s', request.headers['X-Forwarded-For'])
        # response['X-Forwarded-For'] = request.headers['X-Forwarded-For']

    for header in request.headers.keys():
        response[header] = request.headers[header]
    return response

"""

@workflow_app.route('/api/workflow/<job_id>/<task_name>', methods=['GET', 'POST', 'OPTIONS'])
@workflow_app.route('/api/workflow/<job_id>', methods=['GET', 'POST', 'OPTIONS'])
def submit_workflow_request(job_id, task_name=None):
    response = {}
    http_status_code = None

    # Retrieve status of a workflow
    if request.method == 'GET':
        response, http_status_code = workflow_handler.get(job_id, task_name)

    # Submit a new workflow
    elif request.method == 'POST':
        response, http_status_code = workflow_handler.post(job_id, task_name)
            
    elif request.method == 'OPTIONS':
        http_status_code = 204
        response, http_status_code = workflow_handler.options(job_id, task_name)

    return response, http_status_code


@workflow_app.route('/api/workflow/<job_id>/<task_name>/event', methods=['POST'])
def send_to_ga(job_id:str, task_name:str=None):
    response = {}
    http_status_code = None

    if GA_TRACKING_ID is not None:
        try:
            cid = None
            category = 'queryData'
            action = None
            label = None
            
            if 'X-Forwarded-For' in request.headers:
                label = request.headers['X-Forwarded-For']
            else:
                logging.warning("Unable to find 'X-Forwarded-For' header within request")
                label = ''

            if 'X-APBS-Client-ID' in request.headers:
                cid = request.headers['X-APBS-Client-ID']
            else:
                http_status_code = 400
                response['status'] = 'error'
                response['message'] = "Missing 'X-APBS-Client-ID' header in request."
                return response, http_status_code

            task_name = task_name.lower()
            if task_name in ACCEPTED_WORKFLOWS:
                if task_name == 'pdb2pqr':
                    action = 'queryPDB2PQR'
                elif task_name == 'apbs':
                    action = 'queryAPBS'

                user_agent_header = {'User-Agent': request.headers['User-Agent']}
                ga_request_body = f'v=1&tid={GA_TRACKING_ID}&cid={cid}&t=event&ec={category}&ea={action}&el={label}\n'

                logging.debug('GA request body: %s', ga_request_body)
                resp = post('https://www.google-analytics.com/collect', data=ga_request_body, headers=user_agent_header)
                if not resp.ok:
                    resp.raise_for_status
                logging.info('GA event sent: %s', action)

                response['status'] = 'success'
                response['message'] = f'Successful event push: {task_name}'
                http_status_code = 200

            else:
                http_status_code = 400 # bad request
                response['status'] = 'error'
                response['message'] = "Workflow names must be in %s." % str(ACCEPTED_WORKFLOWS)
                logging.error(f"{response['message']} Workflow specified: '{task_name}'.")

        except Exception:
            http_status_code = 500
            response['status'] = 'error'
            response['message'] = "Unexpected error while computing event request. See logs." % str(ACCEPTED_WORKFLOWS)

            logging.error(traceback.format_exc())
    else:
        http_status_code = 400 # bad request
        response['message'] = "Installation not configured with Google Analytics; no ID set."
        logging.error( response['message'] )

    return response, http_status_code