import requests, json

def assert_task_status(task_url: str, job_id: str, jobtype: str):
    # GET: check status of running task
    response = requests.get('%s/%s/%s' % (task_url, job_id, jobtype))
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    json_dict = json.loads(response.content)

    assert json_dict['jobtype'] in json_dict.keys()
    assert set(['jobtype', 'jobid', json_dict['jobtype']]) == json_dict.keys()
    assert set(['status', 'startTime', 'endTime', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()    
    assert json_dict[json_dict['jobtype']]['status'] == 'running'


    # GET: check status of running task (long-poll)
    response = requests.get('%s/%s/%s?wait=true' % (task_url, job_id, jobtype))
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    json_dict = json.loads(response.content)

    assert json_dict['jobtype'] in json_dict.keys()
    assert set(['jobtype', 'jobid', json_dict['jobtype']]) == json_dict.keys()
    assert set(['status', 'startTime', 'endTime', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()

    # GET: check status of completed task
    response = requests.get('%s/%s/%s' % (task_url, job_id, jobtype))
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    json_dict = json.loads(response.content)

    assert json_dict['jobtype'] in json_dict.keys()
    assert set(['jobtype', 'jobid', json_dict['jobtype']]) == json_dict.keys()
    assert set(['status', 'startTime', 'endTime', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()
    assert json_dict[json_dict['jobtype']]['status'] == 'complete'
