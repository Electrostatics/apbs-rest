from __future__ import print_function
from flask import request, Blueprint

import time
from sys import path
from os import getenv, getcwd
from requests import get, post

path.append(getcwd())
from . import task_utils
# from task import task_utils

task_app = Blueprint('task_app', __name__)
task_handler = task_utils.TaskHandler()

TMP_EXEC_HOST = getenv('TMP_EXEC_HOST', 'http://localhost:5005')
END_STATES = ['complete', 'error', None]

@task_app.route('/', methods=['GET'])
@task_app.route('/check/', methods=['GET'])
def is_alive():
    return '', 200

@task_app.route('/api/task/<job_id>/<task_name>', methods=['GET', 'POST'])
def task_action(job_id, task_name):
    response = None
    http_status = None

    # Acquire status of a task
    if request.method == 'GET':
        response, http_status = task_handler.get(job_id, task_name)

    # Submit a task
    elif request.method == 'POST':
        response, http_status = task_handler.post(job_id, task_name)
        
    return response, http_status