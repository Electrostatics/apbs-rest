# from sys import argv
from os import getenv, path, listdir
from requests import post

try:
    import simplejson as json
except:
    import json

JOB_ID       = getenv('JOB_ID', None)
UPLOAD_DIR   = getenv('UPLOAD_DIR', None)
STORAGE_HOST = getenv('STORAGE_HOST', None)

class EnvironmentValueError(ValueError):
    def __init__(self, expression):
        self.expression = 'Missing environment variable %s' % expression

if __name__ == "__main__":

    if JOB_ID is None: raise EnvironmentValueError('JOB_ID')
    if UPLOAD_DIR is None: raise EnvironmentValueError('UPLOAD_DIR')
    if STORAGE_HOST is None: raise EnvironmentValueError('STORAGE_HOST')

    print('Uploading...')
    upload_files = listdir(UPLOAD_DIR)

    # Move status file to end if it is not already. Addresses race condition of status-file uploading before output-file, causing error in CLI
    for file_name in upload_files:
        if file_name.endswith('_status') and upload_files.index(file_name) != len(upload_files)-1:
            upload_files.append(upload_files.pop(upload_files.index(file_name)))
            break

    for file_name in upload_files:
        print('   %s' % file_name)

        # Upload file data to storage service
        object_name = '%s/%s' % (JOB_ID, file_name)
        files = {'file_data': open('%s/%s' % (UPLOAD_DIR, file_name) , 'rb')}
        response = post('%s/%s' % (STORAGE_HOST, object_name), files=files)

        if response.status_code >= 500:
            raise ConnectionError('File %s could not be uploaded. Returned HTTP code %d' % (file_name, response.status_code))
            
    print('...done')