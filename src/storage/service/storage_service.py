from __future__ import print_function
import sys, os, atexit
import pprint as pp
from json import JSONEncoder, loads, dumps
from flask import request, send_from_directory, make_response, Response, Blueprint
# from flask.json import json_encoder, json_decoder
from flask import json
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from urllib3.exceptions import MaxRetryError
from minio.error import ResponseError
# from PDB2PQR_web import app
# import storage_utils
from . import storage_utils
from io import BytesIO

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
@storage_app.route('/check/', methods=['GET'])
def is_Alive():
    return '', 200

@storage_app.route('/api/storage/<job_id>/<file_name>', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@storage_app.route('/api/storage/<job_id>', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
def storage_service(job_id, file_name=None):
    # def storage_service(job_id, file_name=None):
    """Endpoint serving as the gateway to storage bucket"""
    
    if file_name:
        object_name = os.path.join(job_id, file_name)
    # print('%s %s' % (request.method, object_name))

    if request.method == 'GET':
        if file_name:
            ''' Gets single file if file_name is not None '''
            return_json = False
            if 'json' in request.args.keys():
                if request.args['json'].lower() == 'true':
                    return_json = True

            if not return_json:
                '''send_file_from_directory'''
                try:
                    file_path_in_cache = storageClient.fget_object(JOB_BUCKET_NAME, object_name)
                    file_dir = os.path.dirname(file_path_in_cache)
                    # return send_from_directory(file_dir, file_path_in_cache.split('/')[-1])
                    return send_from_directory(file_dir, os.path.basename(file_path_in_cache))
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

        else:
            ''' Sends all files (as tar.gz) to client if no file_name is specified '''
            try:
                # tar files for given job_id
                tarfile_path = storageClient.gzip_job_files(JOB_BUCKET_NAME, job_id)
                jobid_dir = os.path.dirname(tarfile_path)
                
                http_response_code = 200
                response = send_from_directory(jobid_dir, os.path.basename(tarfile_path))
            except:
                response = 'Error in retrieving job contents'
                http_response_code = 500
            finally:
                return response, http_response_code

    elif request.method == 'POST':
        # EXTENSION_WHITELIST = set(['pqr', 'pdb', 'in', 'p'])
        response = 'Success'
        http_response_code = 201

        # pp.pprint(request.files.keys())
        print('request.files keys:')
        for key in request.files.keys():
            print('  ', key)
        try:
            file_data = request.files['file_data']
            # print(type(file_data), flush=True)
        except:
            # file_data = BytesIO(request.data)
            # print(request.data.decode('utf-8'))

            file_data = FileStorage(
                stream=BytesIO(request.data),
                filename=file_name,
            )
            # print(type(file_data))

        if file_data.filename:
            uploaded_file_name = secure_filename(file_data.filename)
            if file_name is None:
                object_name = os.path.join(job_id, uploaded_file_name)
            if file_data.filename and uploaded_file_name:
                etag_str = storageClient.put_object(JOB_BUCKET_NAME, object_name, file_data)

                # Returns internal error code if Minio connection isn't successful
                if etag_str is None:
                    response = "File '%s' could not be uploaded at this time. Please try again later."
                    http_response_code = 500

        return response, http_response_code

    elif request.method == 'DELETE':
        '''
            Removes file(s) from the storage bucket
                If file_name is present, only that file the given job_id is deleted
                Otherwise, ALL FILES for a given job_id are deleted (like deleting a directory)
        '''
        response = ''
        http_response_code = 204

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

        try:
            storageClient.remove_objects(JOB_BUCKET_NAME, object_list)
        except ResponseError:
            http_response_code = 500
            response = 'Request for deletion could not be completed at this time. Please try again later'
        except Exception as err:
            http_response_code = 500
            response = 'Internal error while completing request.'
            print(err, file=sys.stderr) #TODO: change to log message later
        finally:
            return response, http_response_code

    elif request.method == 'OPTIONS':
        options = ['GET', 'POST', 'DELETE']
        response = make_response()
        response = storage_utils.get_request_options(response, options)
        http_response_code = 204
        
        return response, http_response_code
