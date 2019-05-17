from __future__ import print_function
import sys, os, atexit
import pprint as pp
from json import JSONEncoder, loads
from flask import request, send_from_directory, make_response, Response
from werkzeug import secure_filename
from PDB2PQR_web import app
import storageutils

''' 
    Below is the endpoint to interact with the storage container.
    This should be decoupled into its own container in the future.
'''

MINIO_CACHE_DIR  = os.environ.get('STORAGE_CACHE_DIR', '/apbs-rest/.minio_cache')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
JOB_BUCKET_NAME  = os.environ.get('MINIO_JOB_BUCKET', 'jobs')

minioClient = storageutils.get_minio_client(MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
storageCache = storageutils.StorageCache(MINIO_CACHE_DIR, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
atexit.register(storageCache.clear_cache)

@app.route('/api/storage/<job_id>/<file_name>', methods=['GET', 'PUT', 'POST', 'DELETE'])
@app.route('/api/storage/<job_id>', methods=['DELETE'])
def storage_service(job_id, file_name=None):
    # def storage_service(job_id, file_name=None):
    """Endpoint serving as the gateway to storage bucket"""
    
    if file_name:
        object_name = os.path.join(job_id, file_name)
    # print('%s %s' % (request.method, object_name))

    if request.method == 'GET':

        '''send_file_from_directory'''
        file_path_in_cache = storageCache.fget_object(JOB_BUCKET_NAME, object_name)
        file_dir = os.path.dirname(file_path_in_cache)
        return send_from_directory(file_dir, file_path_in_cache.split('/')[-1])
        # return send_from_directory(os.path.dirname(file_path_in_cache), file_path_in_cache)

    elif request.method == 'PUT':
        try:
            payload = loads(request.data)
        except:
            payload = request.data

    elif request.method == 'POST':
        EXTENSION_WHITELIST = set(['pqr', 'pdb', 'in', 'p'])
        pp.pprint(dict(request.files))
        # pp.pprint(request.form['job_id'])
        file_data = request.files['file_data']
        if file_data.filename:
            file_name = secure_filename(file_data.filename)
            print('secure_filename: '+file_name)
            if file_data.filename and file_name:
                storageCache.put_object(JOB_BUCKET_NAME, object_name, file_data)
            # if file_data.filename and allowed_file(file_name, EXTENSION_WHITELIST):
            #     # print('uploading to bucket')
            #     storageCache.put_object(JOB_BUCKET_NAME, object_name, file_data)
            # elif not allowed_file(file_name, EXTENSION_WHITELIST):
            #     return 'Unsupported media type', 415


        # time.sleep(1)
        return 'Success', 201

    elif request.method == 'DELETE':
        object_list = []
        if file_name is None:
            # get list of objects with prefix
            # for each object, delete from bucket
            job_objects = storageCache.list_objects(JOB_BUCKET_NAME, prefix=job_id+'/')
            for obj in job_objects:
                object_list.append(obj.object_name)

        else:
            # delete single object from bucket
            object_list.append(object_name)

        storageCache.remove_objects(JOB_BUCKET_NAME, object_list)

        return 'Success', 204