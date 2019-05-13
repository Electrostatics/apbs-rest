from __future__ import print_function
import os, time, sys
from sys import stdout
from src.aconf import *
from json import JSONEncoder
from flask import make_response
import requests

def get_new_id():
    """Returns a unique identifier string"""
    new_id = str(time.time())
    new_id = new_id.replace('.','')
    return new_id

def get_starttime(jobid, jobtype):
    """Returns the start time for the specified job id and type"""
    starttime = None
    jobtime_path = '%s%s%s/%s_start_time' % (INSTALLDIR, TMPDIR, jobid, jobtype)
    if os.path.exists(jobtime_path):
        fin = open(jobtime_path)
        starttime = float(fin.readline())
    return starttime


def get_endtime(jobid, jobtype):
    """Returns the end time for the specified job id and type"""
    endtime = None
    jobtime_path = '%s%s%s/%s_end_time' % (INSTALLDIR, TMPDIR, jobid, jobtype)
    if os.path.exists(jobtime_path):
        fin = open(jobtime_path)
        endtime = float(fin.readline())
    return endtime

def get_request_options(response, methods_array):
    # response = make_response
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    response.headers['Access-Control-Allow-Methods'] = methods_array
    return response

def get_jobstatusinfo(jobid, jobtype):
    """Returns the status and potential output files for the specified job id and type"""
    job_status = None
    job_progress = []
    job_status_path = '%s%s%s/%s_status' % (INSTALLDIR, TMPDIR, jobid, jobtype)
    if os.path.exists(job_status_path):
        # If status file exists, populate job_status and job_progress
        # with the status and potential output files, respectively
        fin = open(job_status_path, 'r')
        for line in fin:
            line_stripped = line.strip()
            if os.path.exists(line_stripped):
                job_progress.append(line_stripped)
            elif  len(job_progress) == 0:
                job_progress.append(line_stripped)
        fin.close()
        job_status = job_progress[0]

        # Converts the retrieved files to URL-friendly versions
        for i in range(1, len(job_progress)):
            filename = job_progress[i].split('/')[-1]
            # job_progress[i] = '%s%s%s/%s' % (WEBSITE, TMPDIR, jobid, filename)
            job_progress[i] = '%s/%s' % (jobid, filename)
    
    # Print information to be sent (for debugging)
    '''
    print("job_type:     " + str(jobtype))
    print("job_status:   " + str(job_status))
    import sys
    sys.stdout.write("job_progress: ")
    print(job_progress)
    '''

    return job_status, job_progress

def send_to_storage_service(storage_host, job_id, file_list, local_upload_dir):
    if sys.version_info[0] == 2:
        stdout.write('Uploading to storage container... \n')
        stdout.flush()
    elif sys.version_info[0] == 3:
        print('Uploading to storage container... ', end='', flush=True)
        pass

    for f in file_list:
        # print(f)
        stdout.write('    sending %s ...\n' % f)
        # time.sleep(0.5)
        f_name = os.path.join(local_upload_dir, job_id, f)
        files = {'file_data': open(f_name, 'rb')}
        url = '%s/api/storage/%s/%s' % (storage_host, job_id, f)

        response = requests.post(url, files=files)
        
    stdout.write(u'...uploading done \u2713\n\n')
    # stdout.write('  done\n\n')

    pass

def delete_from_storage_service(storage_host, job_id, file_name=None):
    try:
        # code to send delete request
        if file_name is None:
            url = '%s/api/storage/%s' % (storage_host, job_id)
        else:
            url = '%s/api/storage/%s/%s' % (storage_host, job_id, file_name)

        response = requests.delete(url)
        pass
    except Exception as err:
        print(err, file=sys.stderr)