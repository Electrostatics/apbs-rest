import requests, json, time

def assert_task_status(task_url: str, job_id: str, jobtype: str, timeout_minutes: int=10):
    # GET: check status of running task
    response = requests.get('%s/%s/%s' % (task_url, job_id, jobtype))
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    json_dict = json.loads(response.content)

    assert json_dict['jobtype'] in json_dict.keys()
    assert set(['jobtype', 'jobid', json_dict['jobtype']]) == json_dict.keys()
    assert set(['status', 'startTime', 'endTime', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()    
    assert json_dict[json_dict['jobtype']]['status'] == 'running'


    # # GET: check status of running task (long-poll)
    # response = requests.get('%s/%s/%s?wait=true' % (task_url, job_id, jobtype))
    # assert response.status_code == 200
    # assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    # json_dict = json.loads(response.content)

    # assert json_dict['jobtype'] in json_dict.keys()
    # assert set(['jobtype', 'jobid', json_dict['jobtype']]) == json_dict.keys()
    # assert set(['status', 'startTime', 'endTime', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()

    # GET: continually check status of running task till completion
    response = requests.get('%s/%s/%s' % (task_url, job_id, jobtype))
    json_dict = json.loads(response.content)
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    start_time = int(time.time())
    while json_dict[json_dict['jobtype']]['status'] == 'running':
        time.sleep(1) # wait 1 second before checking status again
        response = requests.get('%s/%s/%s' % (task_url, job_id, jobtype))
        json_dict = json.loads(response.content)
        cur_time = int(time.time())
        if cur_time-start_time > (60*timeout_minutes):
            raise TimeoutError("Test job '%s' (%s) took too long...exiting" % (job_id, jobtype))

    # GET: check status of completed task
    response = requests.get('%s/%s/%s' % (task_url, job_id, jobtype))
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    json_dict = json.loads(response.content)

    assert json_dict['jobtype'] in json_dict.keys()
    assert set(['jobtype', 'jobid', json_dict['jobtype']]) == json_dict.keys()
    assert set(['status', 'startTime', 'endTime', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()
    assert json_dict[json_dict['jobtype']]['status'] == 'complete'

def assert_workflow_status(workflow_url: str, job_id: str, jobtype: str, timeout_minutes: int=10):
    # GET: check status of running task
    response = requests.get('%s/%s/%s' % (workflow_url, job_id, jobtype))
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    json_dict = json.loads(response.content)

    assert json_dict['jobtype'] in json_dict.keys()
    assert set(['jobtype', 'jobid', json_dict['jobtype']]) == json_dict.keys()
    assert set(['status', 'startTime', 'endTime', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()    
    assert json_dict[json_dict['jobtype']]['status'] == 'running'

    # GET: continually check status of running task till completion
    response = requests.get('%s/%s/%s' % (workflow_url, job_id, jobtype))
    json_dict = json.loads(response.content)
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    start_time = int(time.time())
    while json_dict[json_dict['jobtype']]['status'] == 'running':
        time.sleep(1) # wait 1 second before checking status again
        response = requests.get('%s/%s/%s' % (workflow_url, job_id, jobtype))
        json_dict = json.loads(response.content)
        cur_time = int(time.time())
        if cur_time-start_time > (60*timeout_minutes):
            raise TimeoutError("Test job '%s' (%s) took too long...exiting" % (job_id, jobtype))

    # GET: check status of completed task
    response = requests.get('%s/%s/%s' % (workflow_url, job_id, jobtype))
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    json_dict = json.loads(response.content)

    assert json_dict['jobtype'] in json_dict.keys()
    assert set(['jobtype', 'jobid', json_dict['jobtype']]) == json_dict.keys()
    assert set(['status', 'startTime', 'endTime', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()
    assert json_dict[json_dict['jobtype']]['status'] == 'complete'
