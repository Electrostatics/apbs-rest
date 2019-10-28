from flask import request, Blueprint
from os import getenv
from sys import stderr
from requests import get, post
from . import workflow_utils

workflow_app = Blueprint('workflow_app', __name__)
workflow_handler = workflow_utils.WorkflowHandler()

END_STATES = ['complete', 'error', None]
TASK_HOST = getenv('TASK_HOST')

@workflow_app.route('/', methods=['GET'])
@workflow_app.route('/check', methods=['GET'])
def is_alive():
    return '', 200

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
