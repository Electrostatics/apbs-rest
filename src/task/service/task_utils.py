import os, time, sys
import requests
try:
    from simplejson import loads
except:
    from json import loads

STORAGE_HOST = os.environ.get('STORAGE_HOST', 'http://localhost:5001')
STORAGE_URL  = os.environ.get('STORAGE_URL' , 'http://localhost:5001/storage')

END_STATES = ['complete', 'error']

def get_starttime(jobid, task_name):
    """Returns the start time for the specified job id and type"""
    starttime = None

    object_name = '%s/%s_start_time' % (jobid, task_name)
    starttime_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    response = requests.get( starttime_url )
    if response.status_code == 200:
        status_str = response.content
        # print(status_str)
        status_str = loads(status_str)[object_name]
        if status_str is not None:
            starttime = float(status_str.split('\n')[0].strip())
        else:
            print(status_str)

    return starttime

def get_endtime(jobid, task_name):
    """Returns the end time for the specified job id and type"""
    endtime = None

    object_name = '%s/%s_end_time' % (jobid, task_name)
    endtime_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    response = requests.get( endtime_url )
    if response.status_code == 200 and get_jobstatus_state(jobid, task_name) in END_STATES:
        status_str = response.content
        status_str = loads(status_str)[object_name]
        if status_str is not None:
            endtime = float(status_str.split('\n')[0].strip())
        else:
            print(status_str)

    else:
        print('    %s job still running' % jobid)

    return endtime

def get_input_files(jobid, task_name):
    input_files = None

    object_name = '%s/%s_input_files' % (jobid, task_name)
    inputfile_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    response = requests.get( inputfile_url )

    if response.status_code == 200:
        obj_content = loads(response.content)[object_name]
        input_files = obj_content.split()
    
    return input_files


def get_output_files(jobid, task_name):
    output_files = None

    object_name = '%s/%s_output_files' % (jobid, task_name)
    outputfile_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    response = requests.get( outputfile_url )

    if response.status_code == 200:
        obj_content = loads(response.content)[object_name]
        output_files = obj_content.split()
    
    return output_files

def get_jobstatus_state(jobid, task_name):
    job_status = None

    object_name = '%s/%s_status' % (jobid, task_name)
    status_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    response = requests.get( status_url )
    if response.status_code == 200:
        status_str = response.content
        status_str = loads(status_str)[object_name]
        if status_str is not None:
            job_status = status_str.split('\n')[0].strip()
        else:
            print(status_str)



    return job_status


def get_jobstatus_info(jobid, task_name):
    """Returns the status and potential output files for the specified job id and type"""
    job_status = None
    job_progress = []

    object_name = '%s/%s_status' % (jobid, task_name)
    status_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    # print('status_url: \n    %s'%status_url)
    response = requests.get( status_url )
    if response.status_code == 200:
        status_str = response.content
        status_str = loads(status_str)[object_name]
        if status_str is not None:
            job_status_text = status_str.split('\n')
            job_status = job_status_text[0]
            for line in job_status_text[1:]:
                line_stripped = line.strip()
                if len(line_stripped) > 0:
                    # print('name: '+line.strip())
                    # print(len(line))
                    job_progress.append(line.strip())
        else:
            print(status_str)

        # Converts the retrieved files to URL-friendly versions
        for i in range(len(job_progress)):
            filename = job_progress[i].split('/')[-1]
            job_progress[i] = '%s/%s' % (jobid, filename)
    
    return job_status, job_progress
