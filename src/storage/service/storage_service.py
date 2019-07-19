from __future__ import print_function
import sys, os, atexit
import pprint as pp
from json import JSONEncoder, loads, dumps
from flask import request, send_from_directory, make_response, Response, Blueprint
# from flask.json import json_encoder, json_decoder
from flask import json
from werkzeug import secure_filename
from urllib3.exceptions import MaxRetryError
# from PDB2PQR_web import app
# import storage_utils
from . import storage_utils

storage_app = Blueprint('storage_app', __name__)

''' 
    Below is the endpoint to interact with the storage container.
    Ideally, this will run within its own container via main.py
'''

MINIO_URL        = os.environ.get('MINIO_URL', 'localhost:9000')
MINIO_CACHE_DIR  = os.environ.get('STORAGE_CACHE_DIR', '/apbs-rest/.minio_cache')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
JOB_BUCKET_NAME  = os.environ.get('MINIO_JOB_BUCKET', 'jobs')

minioClient = storage_utils.get_minio_client(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
storageClient = storage_utils.StorageClient(MINIO_URL, MINIO_CACHE_DIR, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
atexit.register(storageClient.clear_cache)

@storage_app.route('/', methods=['GET'])
@storage_app.route('/check', methods=['GET'])
def is_Alive():
    return '', 200

@storage_app.route('/api/storage/<job_id>/<file_name>', methods=['GET', 'PUT', 'POST', 'DELETE'])
@storage_app.route('/api/storage/<job_id>', methods=['DELETE'])
def storage_service(job_id, file_name=None):
    # def storage_service(job_id, file_name=None):
    """Endpoint serving as the gateway to storage bucket"""
    
    if file_name:
        object_name = os.path.join(job_id, file_name)
    # print('%s %s' % (request.method, object_name))

    if request.method == 'GET':
        return_json = False
        if 'json' in request.args.keys():
            if request.args['json'].lower() == 'true':
                return_json = True

        if not return_json:
            '''send_file_from_directory'''
            # file_path_in_cache = storageClient.fget_object(JOB_BUCKET_NAME, object_name)
            # file_dir = os.path.dirname(file_path_in_cache)
            # return send_from_directory(file_dir, file_path_in_cache.split('/')[-1])

            try:
                file_path_in_cache = storageClient.fget_object(JOB_BUCKET_NAME, object_name)
                file_dir = os.path.dirname(file_path_in_cache)
                return send_from_directory(file_dir, file_path_in_cache.split('/')[-1])
            except MaxRetryError:
                return 'Error in retrieving file\n', 500
            except:
                return 'File %s does not exist\n' % file_name, 404
        else:
            try:
                file_str = storageClient.get_object(JOB_BUCKET_NAME, object_name)
                file_str_json = { object_name: file_str.decode('utf-8') }
                # response = make_response(JSONEncoder().encode(file_str_json))
                response = make_response( dumps(file_str_json) )
                response.headers['Content-Type'] = 'application/json'
                http_response_code = 200
                # return response, http_response_code
            except MaxRetryError:
                json_string = {object_name: None}
                response = make_response(dumps(json_string))
                response.headers['Content-Type'] = 'application/json'
                http_response_code = 500
                # return response, 500
            except Exception as e:
                # import traceback
                # json_string = {object_name: None, 'error': str(e), 'traceback': traceback.format_exc()}
                json_string = {object_name: None}
                response = make_response(dumps(json_string))
                response.headers['Content-Type'] = 'application/json'
                http_response_code = 500
                # return response, 500
            finally:
                return response, http_response_code

    elif request.method == 'PUT':
        try:
            payload = loads(request.data)
        except:
            payload = request.data

    elif request.method == 'POST':
        EXTENSION_WHITELIST = set(['pqr', 'pdb', 'in', 'p'])
        # pp.pprint(dict(request.files))
        # pp.pprint(request.form['job_id'])
        file_data = request.files['file_data']
        if file_data.filename:
            file_name = secure_filename(file_data.filename)
            if file_data.filename and file_name:
                storageClient.put_object(JOB_BUCKET_NAME, object_name, file_data)
            # if file_data.filename and allowed_file(file_name, EXTENSION_WHITELIST):
            #     # print('uploading to bucket')
            #     storageClient.put_object(JOB_BUCKET_NAME, object_name, file_data)
            # elif not allowed_file(file_name, EXTENSION_WHITELIST):
            #     return 'Unsupported media type', 415


        # time.sleep(1)
        return 'Success', 201

    elif request.method == 'DELETE':
        object_list = []
        if file_name is None:
            # get list of objects with prefix
            # for each object, delete from bucket
            job_objects = storageClient.list_objects(JOB_BUCKET_NAME, prefix=job_id+'/')
            for obj in job_objects:
                object_list.append(obj.object_name)

        else:
            # delete single object from bucket
            object_list.append(object_name)

        storageClient.remove_objects(JOB_BUCKET_NAME, object_list)

        return 'Success', 204