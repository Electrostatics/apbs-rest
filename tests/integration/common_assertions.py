import requests, json, time
from pprint import pprint

def assert_task_status(task_url: str, job_id: str, jobtype: str, timeout_minutes: int=10):
    # GET: check status of running task
    time.sleep(3) # Wait 3 seconds before checking status
    response = requests.get('%s/%s/%s' % (task_url, job_id, jobtype))
    # print(response.content)
    # print(json.dumps(response.json(), indent=2))
    print(f'Initial Task response code: {response.status_code}')
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    json_dict = json.loads(response.content)

    # pprint(json_dict)
    assert json_dict['jobtype'] in json_dict.keys()
    assert set(['jobtype', 'jobid', json_dict['jobtype']]) == json_dict.keys()
    # time.sleep(2)
    assert set(['status', 'startTime', 'endTime', 'subtasks', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()    
    assert json_dict[json_dict['jobtype']]['status'] in {'pending', 'running'}


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
    print(f'Task response code (before continuous poll): {response.status_code}')
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    start_time = int(time.time())
    while json_dict[json_dict['jobtype']]['status'] in {'pending', 'running'}:
        time.sleep(1) # wait 1 second before checking status again
        response = requests.get('%s/%s/%s' % (task_url, job_id, jobtype))
        print(response.content)
        assert response.ok
        json_dict = response.json()
        # json_dict = json.loads(response.content)
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
    assert set(['status', 'startTime', 'endTime', 'subtasks', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()
    assert json_dict[json_dict['jobtype']]['status'] == 'complete'

def assert_workflow_status(workflow_url: str, job_id: str, jobtype: str, timeout_minutes: int=10):
    # GET: check status of running task
    time.sleep(3) # Wait 3 seconds before checking status
    response = requests.get('%s/%s/%s' % (workflow_url, job_id, jobtype))
    print(f'Initial Workflow job response code: {response.status_code}')
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    json_dict = json.loads(response.content)

    assert json_dict['jobtype'] in json_dict.keys()
    # pprint(json_dict)
    assert set(['jobtype', 'jobid', json_dict['jobtype']]) == json_dict.keys()
    assert set(['status', 'startTime', 'endTime', 'subtasks', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()    
    assert json_dict[json_dict['jobtype']]['status'] in {'running', 'pending'}

    # GET: continually check status of running task till completion
    response = requests.get('%s/%s/%s' % (workflow_url, job_id, jobtype))
    json_dict = json.loads(response.content)
    print(f'Workflow job response code (before continuous poll): {response.status_code}')
    assert response.status_code == 200
    assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
    start_time = int(time.time())
    while json_dict[json_dict['jobtype']]['status'] in {'pending', 'running'}:
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
    assert set(['status', 'startTime', 'endTime', 'subtasks', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()
    assert json_dict[json_dict['jobtype']]['status'] == 'complete'
