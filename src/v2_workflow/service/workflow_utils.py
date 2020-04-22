import logging
from flask import request, make_response
from os import getenv
from sys import stderr, stdout
from requests import get, post
from json import dumps

TASK_HOST = getenv('TASK_HOST')

class WorkflowHandler:
    def __init__(self):
        pass

    def get(self, job_id, task_name):
        '''
            Workflow Service currently only fulfills APBS and PDB2PQR (single-task) 'workflows'
            As such, GET request simply fetches the task status of the given task_name and
                passes the respective response/status code to the client
        '''
        response = {}
        http_status_code = None

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
    
    def post(self, job_id, task_name):
        response = {}
        http_status_code = None
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
            # for key in request.headers.keys():
            #     print('%s: %s' % (key, request.headers[key]) )
            logging.info(f"sending workflow '{workflow_name}' for job '{job_id}' to the task service")
            user_headers = {
                'User-Agent': request.headers['User-Agent'],
                'X-Forwarded-For': request.headers['X-Forwarded-For']
            }
            if 'X-APBS-Client-ID' in request.headers:
                user_headers['X-APBS-Client-ID'] = request.headers['X-APBS-Client-ID']
            logging.debug( dumps(user_headers, indent=2) )
            task_response = post('%s/api/task/%s/%s%s' % (TASK_HOST, job_id, workflow_name, infile_url_query), json=task_params, headers=user_headers)
            if task_response.status_code == 202:
                http_status_code = task_response.status_code
                response = task_response.json()

            #TODO: write handler for a fail case if Task Service sends non-202 response
            #Solution: just pass along status/response from task service
            elif task_response.status_code in [400, 500]: # may want to predefine [400, 500] to avoid reinstantiating per request
                logging.error('Received error status code from Task Service: %d', task_response.status_code)
                http_status_code = task_response.status_code
                response = task_response.json()

                logging.error('Response from Task Service: \n%s', str(task_response.json()))
            else:
                # may handle differently in future
                http_status_code = task_response.status_code
                response = task_response.json()

        except Exception as e:
            http_status_code = 500
            print('Error: %s' % e, file=stderr)

        stdout.flush()
        stderr.flush()
        return response, http_status_code

    def options(self, job_id, task_name):
        options = ['GET', 'POST']
        response = make_response()
        response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
        response.headers['Access-Control-Allow-Methods'] = options
        http_status_code = 204
        return response, http_status_code