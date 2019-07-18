from __future__ import print_function
from flask import request, Blueprint
import uuid
from random import choices
from string import ascii_lowercase, digits

uid_gen = Blueprint('uid_gen', __name__)

''' 
    Below is the endpoint to generate a unique job ID string.
    This would be used to provide a client with an ID with which
        to start a workflow job.
'''

@uid_gen.route('/', methods=['GET'])
@uid_gen.route('/check/', methods=['GET'])
def liveness():
    """Probes server to check if alive"""
    return '', 200

@uid_gen.route('/api/uid/', methods=['GET'])
def uid_generator():
    """On GET, generate a unique ID string"""
    if request.method == 'GET':
        # job_id = uuid.uuid4().hex
        # job_id = uuid.uuid4().int
        job_id = ''.join(choices(ascii_lowercase+digits, k=10)) # random 10-character alphanumeric string

        http_code = 200
        response = {'job_id': str(job_id)}
        return response, http_code