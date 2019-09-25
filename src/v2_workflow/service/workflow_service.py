from flask import request, Blueprint
from os import getenv
from sys import stderr
from requests import get, post

workflow_app = Blueprint('workflow_app', __name__)

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

    if request.method == 'POST':
        try:
            request_json = request.get_json()

            # Returns a bad request error if missing 1) both workflow name *and* task name or 2) form data
            if ('workflow' not in request_json and task_name is None) or 'form' not in request_json:
                http_status_code = 400
                response['error'] = ""
                if 'form' not in request_json:
                    response['error'] = "Missing key/value entry 'form' within request JSON\n"
                if 'workflow' not in request_json:
                    response['error'] = "Missing key/value entry 'workflow' within request JSON\n"
                if task_name is None:
                    response['error'] = "Did not specify a task_name in the URL. This or a 'workflow' param in the JSON is required\n"

            # Dubs the workflow_name as the passed task_name if missing in request
            if 'workflow' in request_json:                
                workflow_name = request_json['workflow']
            else:
                workflow_name = task_name

            task_params = request_json['form']
            # http_status_code = 202

            # If task_params includes a 'filename' field, use of APBS infile is assumed
            infile_url_query = ''
            if 'filename' in task_params and workflow_name == 'apbs':
                infile_url_query = '?infile=true'
            
            # Send the appropriate task parameters to the Task Service
            print(f"sending workflow '{workflow_name}' for job '{job_id}' to the task service")
            task_response = post('%s/api/task/%s/%s%s' % (TASK_HOST, job_id, workflow_name, infile_url_query), json=task_params)
            if task_response.status_code == 202:
                http_status_code = task_response.status_code
                response = task_response.json()
            #TODO: write handler for a fail case if Task Service sends non-202 response

        except Exception as e:
            http_status_code = 500
            print('Error: %s' % e, file=stderr)

    elif request.method == 'GET':
        '''
            Workflow Service currently only fulfills APBS and PDB2PQR (single-task) 'workflows'
            As such, GET request simply fetches the task status of the given task_name and
                passes the respective response/status code to the client
        '''

        # Construct error response if given invalid task
        if task_name not in ['apbs', 'pdb2pqr']:
            response = {
                'status': None,
                'error': f"task type '{task_name}' does not exist or is not implemented"
            }
            http_status_code = 404

        # Get the task response from the Task Service, pass the response/status code
        else:
            wait_on_task = False
            if 'wait' in request.args.keys():
                if request.args['wait'].lower() == 'true':
                    # return {'args': request.args['wait']}
                    wait_on_task = True
            task_status_response = get('%s/api/task/%s/%s?wait=%s' % (TASK_HOST, job_id, task_name, wait_on_task))

            http_status_code = task_status_response.status_code
            response = task_status_response.json()

        return response, http_status_code
            
    elif request.method == 'OPTIONS':
        http_status_code = 204

    return response, http_status_code
