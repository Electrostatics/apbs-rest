from __future__ import print_function
from flask import request, Blueprint
import uuid

uid_gen = Blueprint('uid_gen', __name__)

''' 
    Below is the endpoint to generate a unique job ID string.
    This would be used to provide a client with an ID with which
        to start a workflow job.
'''

@uid_gen.route('/api/uid', methods=['GET'])
def uid_generator():
    """On GET, generate a unique ID string"""
    if request.method == 'GET':
        job_id = uuid.uuid4().hex
        response = {'job_id': job_id}
        return response