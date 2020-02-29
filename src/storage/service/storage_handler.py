import sys, os
from json import JSONEncoder, loads, dumps
from io import BytesIO

from flask import request, send_from_directory, make_response
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from urllib3.exceptions import MaxRetryError
from minio.error import ResponseError

from . import storage_utils

MINIO_URL        = os.environ.get('MINIO_URL', 'localhost:9000')
MINIO_CACHE_DIR  = os.environ.get('STORAGE_CACHE_DIR', '/apbs-rest/.minio_cache')
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
JOB_BUCKET_NAME  = os.environ.get('MINIO_JOB_BUCKET', 'jobs')

class StorageHandler:
    def __init__(self):
        self.minioClient = storage_utils.get_minio_client(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
        self.storageClient = storage_utils.StorageClient(MINIO_URL, MINIO_CACHE_DIR, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
    
    def get(self, object_name, job_id, file_name=None):
        if file_name:
            ''' Gets single file if file_name is not None '''
            return_json = False
            view_in_browser = False

            if 'json' in request.args.keys():
                if request.args['json'].lower() == 'true':
                    return_json = True
            if 'view' in request.args.keys():
                if request.args['view'].lower() == 'true':
                    view_in_browser = True

            if not return_json:
                '''send_file_from_directory'''
                try:
                    file_path_in_cache = self.storageClient.fget_object(JOB_BUCKET_NAME, object_name)
                    file_dir = os.path.dirname(file_path_in_cache)

                    http_response_code = 200
                    response = send_from_directory(file_dir, os.path.basename(file_path_in_cache))
                    if view_in_browser:
                        response.headers['Content-Disposition'] = 'inline'
                        response.headers['Content-Type'] = 'text/plain; charset=utf-8'
                    else:
                        response.headers['Content-Disposition'] = 'attachment; filename="%s"' % file_name
                    
                except MaxRetryError:
                    response = 'Error in retrieving file\n'
                    http_response_code = 500
                except:
                    response = 'File %s does not exist\n' % file_name
                    http_response_code = 404
                finally:
                    return response, http_response_code
                    
            else:
                try:
                    file_str = self.storageClient.get_object(JOB_BUCKET_NAME, object_name)
                    file_str_json = { object_name: file_str.decode('utf-8') }
                    response = make_response( dumps(file_str_json) )
                    response.headers['Content-Type'] = 'application/json'
                    http_response_code = 200

                except MaxRetryError:
                    json_string = {object_name: None}
                    response = make_response(dumps(json_string))
                    response.headers['Content-Type'] = 'application/json'
                    http_response_code = 500

                except Exception as e:
                    # import traceback
                    # json_string = {object_name: None, 'error': str(e), 'traceback': traceback.format_exc()}
                    json_string = {object_name: None}
                    response = make_response(dumps(json_string))
                    response.headers['Content-Type'] = 'application/json'
                    http_response_code = 500

                finally:
                    return response, http_response_code

        else:
            ''' Sends all files (as tar.gz) to client if no file_name is specified '''
            try:
                # tar files for given job_id
                tarfile_path = self.storageClient.gzip_job_files(JOB_BUCKET_NAME, job_id)
                if tarfile_path is not None:
                    jobid_dir = os.path.dirname(tarfile_path)
                    http_response_code = 200
                    response = send_from_directory(jobid_dir, os.path.basename(tarfile_path))
                else:
                    http_response_code = 404
                    response = 'Requested ID %s has no associated files' % job_id
            except Exception as e:
                response = "Error in retrieving contents for ID '%s'" % job_id
                http_response_code = 500
                print(e) #TODO: change to log message later
            finally:
                return response, http_response_code

        


    def post(self, object_name, job_id, file_name=None):
        # EXTENSION_WHITELIST = set(['pqr', 'pdb', 'in', 'p'])
        response = { 'status': None, 'message': None }
        # response = 'Success'
        http_response_code = 201

        try:
            file_data = request.files['file_data']
        except KeyError:
            # fallback in case file data is in body
            file_data = FileStorage(
                stream=BytesIO(request.data),
                filename=file_name,
            )
        except:
            http_response_code = 500
            response['status'] = 'failed'
            response['message'] = "Could not find data to upload.  File data should be in request body or form files with key='file_data'"
            return response, http_response_code

        if file_data.filename:
            uploaded_file_name = secure_filename(file_data.filename)
            if file_name is None:
                object_name = os.path.join(job_id, uploaded_file_name)
            if file_data.filename and uploaded_file_name:
                etag_str = self.storageClient.put_object(JOB_BUCKET_NAME, object_name, file_data)

                # Returns internal error code if Minio connection isn't successful
                if etag_str is None:
                    response['status'] = 'failed'
                    response['message'] = "File '%s' could not be uploaded at this time. Please try again later." % (file_name)
                    http_response_code = 500
                else:
                    # Create success response
                    response['status'] = 'success'
                    response['message'] = "Data uploaded to %s/%s." % (job_id, file_name)
                    http_response_code = 201

        return response, http_response_code


    def delete(self, object_name, job_id, file_name=None):
        '''
            Removes file(s) from the storage bucket
                If file_name is present, only that file the given job_id is deleted
                Otherwise, ALL FILES for a given job_id are deleted (like deleting a directory)
        '''
        response = { 'status': None, 'message': None }
        http_response_code = 204

        object_list = []
        if file_name is None:
            # get list of objects with prefix
            # for each object, delete from bucket
            job_objects = self.storageClient.list_objects(JOB_BUCKET_NAME, prefix=job_id+'/')
            for obj in job_objects:
                object_list.append(obj.object_name)

        else:
            # delete single object from bucket
            object_list.append(object_name)

        try:
            self.storageClient.remove_objects(JOB_BUCKET_NAME, object_list)
            # http_response_code = 200 #TODO: adjust unit tests before changing code to 200
            # response['status'] = 'success'
            # response['message'] = 'Object(s) successfully deleted'
            http_response_code = 204
            response = ''
        except ResponseError:
            http_response_code = 500
            response['status'] = 'failed'
            response['message'] = 'Request for deletion could not be completed at this time. Please try again later'
        except Exception as err:
            http_response_code = 500
            response['status'] = 'failed'
            response['message'] = 'Internal error while completing request.'
            print(err, file=sys.stderr) #TODO: change to log message later
        finally:
            return response, http_response_code


    def options(self):
        options = ['GET', 'POST', 'DELETE']
        response = make_response()
        response = storage_utils.get_request_options(response, options)
        http_response_code = 204
        
        return response, http_response_code
                