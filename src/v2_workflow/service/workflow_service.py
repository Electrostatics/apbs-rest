from flask import request, Blueprint
from os import getenv
from sys import stderr
from requests import get, post

# from . import workflow_utils
import time, json

workflow_app = Blueprint('workflow_app', __name__)

# WORKFLOW_DATABASE = getenv('WORKFLOW_DATABASE', 'http://localhost:3306')
END_STATES = ['complete', 'error', None]
TASK_HOST = getenv('TASK_HOST')


@workflow_app.route('/api/workflow/<job_id>/<task_name>', methods=['GET', 'POST', 'OPTIONS'])
@workflow_app.route('/api/workflow/<job_id>', methods=['GET', 'POST', 'OPTIONS'])
def submit_workflow_request(job_id, task_name=None):
    # 
    response = {}
    http_status_code = None

    # from pprint import pprint
    # pprint(request.data)

    if request.method == 'POST':
        '''==========================================='''
        '''==========================================='''
        # try:
        #     request_json = request.get_json()
        #     form_list = request_json['form']
        #     if 'workflow' in request_json:
        #         task_list = request_json['workflow']
        #     elif task_name is not None:
        #         task_list = [task_name]
        #     else:
        #         http_status_code = 400
        #         response = "Request missing the 'workflow' parameter in JSON, or you did not specify a task in the URL."
        #         return response, http_status_code
            
        #     # Submit each task directly to the task service
        #     #TODO: setup a workflow service using TES
        #     http_status_code = 202
        #     for task, form in zip(task_list, form_list):
        #         task_response = post('%s/api/task/%s/%s' % (TASK_HOST, job_id, task), json=json.dumps(form) )
        #         if task_response.status_code != 202:
        #             http_status_code = 202
        #             response = task_response.json()

        # except Exception as e:
        #     print(e)
        #     http_status_code = 500

        '''==========================================='''
        '''==========================================='''

        try:
            request_json = request.get_json()

            if ('workflow' not in request_json and task_name is None) or 'form' not in request_json:
                http_status_code = 400
                response['error'] = ""
                if 'form' not in request_json:
                    response['error'] = "Missing key/value entry 'form' within request JSON\n"
                if 'workflow' not in request_json:
                    response['error'] = "Missing key/value entry 'workflow' within request JSON\n"
                if task_name is None:
                    response['error'] = "Did not specify a task_name in the URL. This or a 'workflow' param in the JSON is required\n"

            if 'workflow' in request_json:                
                workflow_name = request_json['workflow']
            else:
                workflow_name = task_name

            task_params = request_json['form']
            http_status_code = 202
            
            print(f"sending workflow '{workflow_name}' for job '{job_id}' to the task service")
            task_response = post('%s/api/task/%s/%s' % (TASK_HOST, job_id, workflow_name), json=task_params)
            if task_response.status_code == 202:
                http_status_code = task_response.status_code
                response = task_response.json()
        except Exception as e:
            http_status_code = 500
            print('Error: %s' % e, file=stderr)


        '''==========================================='''
        '''==========================================='''


    elif request.method == 'GET':
        # if task_name not in ['apbs', 'pdb2pqr']:
        #     response = {
        #         'status': None,
        #         'error': f"task type '{task_name}' does not exist or is not implemented"
        #     }
        #     http_status_code = 404
        #     # return response, 404
        #     print('happening here')
        # else:
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

