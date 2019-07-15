from __future__ import print_function
import requests, time, sys, os
from os import getenv
from json import loads

def allowed_file(filename, valid_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in valid_extensions

def get_request_options(response, methods_array):
    # response = make_response
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    response.headers['Access-Control-Allow-Methods'] = methods_array
    return response

def get_new_id():
    """Returns a unique identifier string"""
    new_id = None
    try:
        response = requests.get('%s/api/uid' % getenv('ID_HOST'))
        new_id = loads(response.content)['job_id']
    except:
        new_id = str(time.time())
        new_id = new_id.replace('.','')
        
    return new_id


def send_to_storage_service(storage_host, job_id, file_list, local_upload_dir):
    if sys.version_info[0] == 2:
        sys.stdout.write('Uploading to storage container... \n')
        sys.stdout.flush()
    elif sys.version_info[0] == 3:
        print('Uploading to storage container... ', end='', flush=True)
        pass

    successful_upload = []
    for f in file_list:
        # print(f)
        sys.stdout.write('    sending %s ...\n' % f)
        # time.sleep(0.5)
        f_name = os.path.join(local_upload_dir, job_id, f)
        files = {'file_data': open(f_name, 'rb')}
        url = '%s/api/storage/%s/%s' % (storage_host, job_id, f)

        response = requests.post(url, files=files)
        print('    status code: '+str(response.status_code))

        if response.status_code >= 200 and response.status_code < 300:
            successful_upload.append(True)
        else:
            successful_upload.append(False)
            
        
    sys.stdout.write(u'...uploading done \u2713\n\n')
    # stdout.write('  done\n\n')
    
    return successful_upload