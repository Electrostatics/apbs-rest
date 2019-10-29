import os, atexit
from flask import request, Blueprint

from . import storage_handler
from . import storage_utils

storage_app = Blueprint('storage_app', __name__)
storageHandler = storage_handler.StorageHandler()
atexit.register(storageHandler.storageClient.clear_cache)

''' 
    Below are the endpoints which interact with the storage container.
'''

@storage_app.route('/', methods=['GET'])
@storage_app.route('/check/', methods=['GET'])
def is_Alive():
    return '', 200

@storage_app.route('/api/storage/<job_id>/<file_name>', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@storage_app.route('/api/storage/<job_id>', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
def storage_service(job_id, file_name=None):
    """Endpoint serving as the gateway to storage bucket"""
    object_name = None
    if file_name:
        object_name = os.path.join(job_id, file_name)

    if request.method == 'GET':
        response, http_response_code = storageHandler.get(object_name, job_id, file_name)

    elif request.method == 'POST':
        response, http_response_code = storageHandler.post(object_name, job_id, file_name)

    elif request.method == 'DELETE':
        '''
            Removes file(s) from the storage bucket
                If file_name is present, only that file the given job_id is deleted
                Otherwise, ALL FILES for a given job_id are deleted (like deleting a directory)
        '''
        response, http_response_code = storageHandler.delete(object_name, job_id, file_name)

    elif request.method == 'OPTIONS':
        response, http_response_code = storageHandler.options()
        
    return response, http_response_code