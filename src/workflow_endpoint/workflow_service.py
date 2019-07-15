from flask import request, Blueprint
from os import getenv
from requests import get, post

from . import workflow_utils
import time, json, mysql.connector

workflow_app = Blueprint('workflow_app', __name__)

# WORKFLOW_DATABASE = getenv('WORKFLOW_DATABASE', 'http://localhost:3306')
END_STATES = ['complete', 'error', None]

DATABASE_HOST      = getenv('DATABASE_HOST')
DATABASE_PORT      = getenv('DATABASE_PORT')
DATABASE_DBNAME    = getenv('DATABASE_NAME')
DATABASE_USER      = getenv('DATABASE_USER')
DATABASE_PASSWORD  = getenv('DATABASE_PASSWORD')
DATABASE_TABLE     = getenv('DATABASE_TABLE')

@workflow_app.route('/api/workflow/<job_id>/<task_name>', methods=['GET', 'POST', 'OPTIONS'])
@workflow_app.route('/api/workflow/<job_id>', methods=['GET', 'POST', 'OPTIONS'])
def submit_workflow_request(job_id, task_name=None):
    # 
    response = {}
    http_status_code = None
    cnx = mysql.connector.connect(
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        database=DATABASE_DBNAME
    )

    # from pprint import pprint
    # pprint(request.data)

    if request.method == 'POST':
        task_no = None
        if 'task' in request.args.keys():
            try:
                task_no = int(request.args['task'])
            except:
                http_status_code = 400
                response = "task argument must be an integer"
                return response, http_status_code

        workflow_string = ''
        # Parse workflow tasks into single string for database
        if 'workflow' in request.data:
            workflow_order = request.data['workflow']
            # for task in workflow_order:
            for i in range(len(workflow_order)):
                task = workflow_order[i]
                if i < len(workflow_order)-1:
                    workflow_string += '%s;' % task
                else:
                    workflow_string += '%s' % task
        else:
            workflow_string = task_name

        if task_no == 0 or task_no is None:
            workflow_status = 'pending'
            task_status = 'pending'
            current_task = 0

            form_list = json.dumps( request.data['form'] )
            empty_output_list = json.dumps( [] )

            query = f"INSERT INTO {DATABASE_TABLE} VALUES ('{job_id}', '{workflow_string}', '{workflow_status}', {current_task}, '{task_status}', '{form_list}', '{empty_output_list}');"
            cursor = cnx.cursor()
            cursor.execute(query)
            cursor.close()
            cnx.commit()

        elif task_no > 0:
            query = f"SELECT workflow, workflow_status, task_params, task_output FROM {DATABASE_TABLE} WHERE job_id='{job_id}'"

            task_status = 'pending'
            current_task = task_no
            form_list = json.dumps( request.data['form'] )
            empty_output_list = json.dumps( [] )

            # get current workflow, status, params, and output
            # parse into workable data structures
            # append new task data into each
            # update database with new values for monitor to pick up 
            cursor = cnx.cursor()
            cursor.execute(query)

            workflow, workflow_status, task_params, task_output = cursor.fetchone()
            cursor.close()

            wf_split = workflow.split(';')
            wf_split.append(task_name)
            param_list = json.loads(task_params)
            param_list.append(request.data['form'][0])
            output_list = json.loads(task_output)
            # output_list.append([])

            workflow = ';'.join(wf_split)
            workflow_status = 'running'
            param_list = json.dumps(param_list)
            output_list = json.dumps(output_list)

            # print(type(request.data['form']))
            # print(request.data['form'])
            # print()
            # print(param_list)
            # print()
            # print(output_list)
            # print()
            
            # query = f"UPDATE {DATABASE_TABLE} SET workflow='{workflow}', workflow_status='{workflow_status}', task_status='{task_status}', task_params='{param_list}', task_output='{output_list}' WHERE job_id='{job_id}'"
            query = f"UPDATE {DATABASE_TABLE} SET workflow='{workflow}', workflow_status='{workflow_status}', task_status='{task_status}', task_params='{param_list}' WHERE job_id='{job_id}'"
            # print(query)
            cursor = cnx.cursor()
            cursor.execute(query)
            cursor.close()
            cnx.commit()


        http_status_code = 202

    elif request.method == 'GET':
        if task_name not in ['apbs', 'pdb2pqr']:
            response = {
                'status': None,
                'error': f"task type '{task_name}' does not exist or is not implemented"
            }
            http_status_code = 404
            # return response, 404
        else:
        # if task_name in ['apbs', 'pdb2pqr']:
            END_STATES = ['complete', 'error']
            progress   = None
            run_state  = None
            start_time = None
            end_time   = None
            response   = {}
            wait_on_task = False
            task_no    = None

            if 'wait' in request.args.keys():
                if request.args['wait'].lower() == 'true':
                    # return {'args': request.args['wait']}
                    wait_on_task = True
            if 'task' in request.args.keys():
                try:
                    task_no = int(request.args['task'])
                except:
                    # task_no request.args['task']
                    # if task_no not in ['apbs', 'pdb2pqr']:
                    http_status_code = 400
                    response = "task argument must be an integer"
                    return response, http_status_code

            workflow_info_obj = workflow_utils.WorkflowInfo(job_id, cnx)

            # NOTE: can later optimize to only get end_time if state isn't 'running'
            # job_info    = workflow_utils.get_workflow_info(job_id, cnx)
            # start_time  = workflow_utils.extract_starttime(job_info, task_name)
            # end_time    = workflow_utils.extract_endtime(job_info, task_name)
            # run_state   = workflow_utils.extract_task_state(job_info, task)
            # progress    = workflow_utils.extract_task_output_files(job_info)

            if workflow_info_obj.workflow_info is not None:
                # print(type(task_no))
                # print(task_no)
                # print(type(task_no))
                job_info    = workflow_info_obj.workflow_info
                start_time  = workflow_info_obj.get_starttime(task_index=task_no)
                end_time    = workflow_info_obj.get_endtime(task_index=task_no)
                run_state   = workflow_info_obj.get_task_state(task_index=task_no)
                progress    = workflow_info_obj.get_task_output_files(task_index=task_no)
                # run_state, progress = workflow_utils.get_jobstatus_info(job_id, task_name)

                if run_state not in END_STATES and wait_on_task:
                    # while run_state not in END_STATES:
                    #     time.sleep(1)
                    #     run_state = workflow_utils.get_jobstatus_state(job_id, task_name)
                    # start_time  = workflow_utils.get_starttime(job_id, task_name)
                    # end_time    = workflow_utils.get_endtime(job_id, task_name)
                    # run_state, progress = workflow_utils.get_jobstatus_info(job_id, task_name)
                    while run_state not in END_STATES:
                        time.sleep(1)
                        workflow_info_obj.refresh()
                        run_state = workflow_info_obj.get_task_state(task_index=task_no)
                    start_time  = workflow_info_obj.get_starttime(task_index=task_no)
                    end_time  = workflow_info_obj.get_endtime(task_index=task_no)
                    run_state  = workflow_info_obj.get_task_state(task_index=task_no)
                    progress  = workflow_info_obj.get_task_output_files(task_index=task_no)

                response['jobid'] = job_id
                if run_state is None:
                    response['error'] = 'Task does not exist'
                    
                if task_name is not None:
                    response[task_name] = {
                        'status':    run_state,
                        # 'files':     progress[1:],
                        'files':     progress,
                        'startTime': start_time,
                        'endTime':   end_time
                    }
                else:
                    # status_list
                    task_name = workflow_info_obj.workflow_str.split(';')[workflow_info_obj.current_task_index]
                    response[task_name] = {
                        'status':    run_state,
                        # 'files':     progress[1:],
                        'files':     progress,
                        'startTime': start_time,
                        'endTime':   end_time
                    }
                    

                http_status_code = 200
                # return response, 200
            else:
                http_status_code = 404
                response = {
                    'status': None,
                    'error': f"job_id '{workflow_info_obj.job_id}' does not exist"
                }
        # else:


    elif request.method == 'OPTIONS':
        # response = make_response(JSONEncoder().encode(json_response))
        # response = jobutils.get_request_options(response, 'POST')
        # response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
        http_status_code = 204

    cnx.close()
    return response, http_status_code

