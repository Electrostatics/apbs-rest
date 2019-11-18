import requests, json, uuid, pprint, tarfile, os
import prepare_tests
import common_assertions

APBS_HOST = os.getenv('APBS_HOST')
if APBS_HOST is None:
    raise EnvironmentError('Environment variable APBS_HOST is not set')

APBS_URL = 'http://%s' % (APBS_HOST)
apbs_adapter = requests.adapters.HTTPAdapter(max_retries=3)

def test_liveness():
    # ID service
    r_slash = requests.get('%s/id/' % APBS_URL)
    r_check = requests.get('%s/id/check' % APBS_URL)
    assert r_slash.status_code == 200
    assert r_check.status_code == 200
    # r_slash = requests.get('%s/storage/' % APBS_URL)
    # r_check = requests.get('%s/task/check' % APBS_URL)
    # assert r_slash.status_code == 200
    # assert r_check.status_code == 200

    # Main website
    response = requests.get(APBS_URL)
    assert response.status_code == 200

def test_id_service():
    '''
        GET:
            /id
                Success: 200
            /id/
                Success: 200
    '''
    url = '%s/id' % APBS_URL
    # session = requests.Session()
    # session.mount('%s/id/' % APBS_URL, apbs_adapter)
    # response = session.get('%s/id/' % APBS_URL)
    ''' /id '''
    response = requests.get(url)
    assert response.status_code == 200
    json_dict = json.loads(response.content)
    assert len(json_dict.keys()) == 1
    assert 'job_id' in json_dict

    ''' /id/ '''
    response = requests.get('%s/' % url)
    assert response.status_code == 200
    json_dict = json.loads(response.content)
    assert len(json_dict.keys()) == 1
    assert 'job_id' in json_dict

def test_storage_service():
    '''
        Methods: GET, POST, DELETE, OPTIONS
    '''
    job_id = 'pytest-%s' % uuid.uuid4().hex[:8]
    url = '%s/storage' % APBS_URL
    object_name = 'sample_text.txt'

    job_id_url = '%s/%s' % (url, job_id)
    req_url = '%s/%s/%s' % (url, job_id, object_name)
    # print(req_url)

    # GET: nonexistent file
    response = requests.get(req_url)
    body = response.content.decode('utf-8')
    assert response.status_code == 404
    assert body == 'File %s does not exist\n' % object_name

    # GET: nonexistent directory
    response = requests.get(job_id_url)
    body = response.content.decode('utf-8')
    assert response.status_code == 404
    assert body == 'Requested ID %s has no associated files' % job_id

    # POST: new file, name it 'sample_text.txt'
    response = requests.post(req_url, data='hello world')
    assert response.status_code == 201

    # GET: file 'sample_text.txt'
    response = requests.get(req_url)
    body = response.content.decode('utf-8')
    assert response.status_code == 200
    # assert body == 'hello worrrld'

    #TODO: GET: all files for nonexistent job_id file
    # GET: all files for specific job_id file; should return a tarfile
    response = requests.get( job_id_url )
    print("job_id_url:", job_id_url)
    tarfile_name = 'sample_tar.tar.gz'
    # assert os.path.exists(tarfile_name) == False
    assert response.status_code == 200
    with open(tarfile_name, 'wb') as fout:
        print(type(response.content))
        fout.write(response.content)
    assert tarfile.is_tarfile(tarfile_name) == True
    os.remove(tarfile_name)

    # DELETE: file 'sample_text.txt'
    response = requests.delete(req_url)
    assert response.status_code == 204

    #TODO: DELETE: entire job_id directory
    # response = requests.delete( job_id_url )
    #TODO: DELETE: nonexistent file
    #TODO: DELETE: nonexistent job_id contents

    # OPTIONS: available options within response header
    response = requests.options(req_url)
    assert response.status_code == 204
    assert response.headers['Access-Control-Allow-Headers'] == 'x-requested-with'
    assert response.headers['Access-Control-Allow-Methods'] == str(['GET', 'POST', 'DELETE'])

def test_task_service():
    job_id = 'pytest-%s' % uuid.uuid4().hex[:8]
    task_url = '%s/task' % APBS_URL
    pdb_id = '1a1p'

    try:
        # GET: nonexistent task for valid taskname
        dummy_job_id = 'nonsense_id'
        # url = '%s/%s/pdb2pqr' % (task_url, dummy_job_id)
        print('%s/%s/pdb2pqr' % (task_url, dummy_job_id))
        response = requests.get('%s/%s/pdb2pqr' % (task_url, dummy_job_id))
        assert response.status_code == 200
        assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
        json_dict = json.loads(response.content)

        assert json_dict['jobtype'] in json_dict.keys()
        assert set(['jobtype', 'error', 'jobid', json_dict['jobtype']]) == json_dict.keys()
        assert set(['status', 'startTime', 'endTime', 'files', 'inputFiles', 'outputFiles']) ==  json_dict[json_dict['jobtype']].keys()
        
        # GET: nonexistent task for invalid taskname
        response = requests.get('%s/%s/nonexistent_task_name' % (task_url, dummy_job_id))
        assert response.status_code == 404
        assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
        json_dict = json.loads(response.content)
        assert set(['error', 'status']) == json_dict.keys()
        assert json_dict['status'] == None

        # POST: invalid taskname
        # url = '%s/%s/nonexistent_task_name' % (task_url, dummy_job_id)
        params = prepare_tests.prepare_task_v1('nonexistent_task_name', '1a1p')
        response = requests.post('%s/%s/nonexistent_task_name' % (task_url, dummy_job_id), json=params)
        assert response.status_code == 400
        assert 'Content-Type' in response.headers.keys() and response.headers['Content-Type'] == 'application/json'
        json_dict = json.loads(response.content)
        assert 'error' in json_dict.keys()

        ''' 
            PDB2PQR
        '''
        #TODO: POST: PDB2PQR task
        params = prepare_tests.prepare_task_v1('pdb2pqr', pdb_id='1a1p')
        response = requests.post('%s/%s/pdb2pqr' % (task_url, job_id), json=params)
        assert response.status_code == 202
        json_dict = json.loads(response.content)
        assert 'accepted' in json_dict.keys()

        # GET: check status of running task
        # GET: check status of running task (long-poll)
        # GET: check status of completed task
        common_assertions.assert_task_status(task_url, job_id, 'pdb2pqr')
        
        # Remove contents from bucket
        requests.delete('%s/storage/%s' % (APBS_URL, job_id)) 

        ''' 
            APBS
        '''
        #TODO: POST: APBS task
        infile_name = '1a1p.in'
        with open('../sample_input/1a1p.in', 'r') as fin:
            apbs_infile_data = fin.read()
            response = requests.post('%s/storage/%s/1a1p.in' % (APBS_URL, job_id), data=apbs_infile_data)
            assert response.status_code == 201
        with open('../sample_input/1a1p.pqr', 'r') as fin:
            apbs_pqr_data = fin.read()
            response = requests.post('%s/storage/%s/1a1p.pqr' % (APBS_URL, job_id), data=apbs_pqr_data)
            assert response.status_code == 201
        params = prepare_tests.prepare_task_v1('apbs', infile_name=infile_name)
        response = requests.post('%s/%s/apbs?infile=true' % (task_url, job_id), json=params)
        assert response.status_code == 202
        json_dict = json.loads(response.content)
        assert 'accepted' in json_dict.keys()
        
        # GET: check status of running task
        # GET: check status of running task (long-poll)
        # GET: check status of completed task
        common_assertions.assert_task_status(task_url, job_id, 'apbs')


    finally:
        # Remove contents of the job_id from bucket
        requests.delete('%s/storage/%s' % (APBS_URL, job_id))

def test_workflow_service():
    job_id = 'pytest-%s' % uuid.uuid4().hex[:8]
    workflow_url = '%s/workflow' % APBS_URL
    # pdb_id = '1a1p'
    job_id_url = '%s/%s' % (workflow_url, job_id)
    
    try:
            
        """version 1 (to be deprecated as we overhaul)"""


        """
            version 2
        """ 

        '''Specify workflow in URL'''

        # TODO: POST: PDB2PQR workflow


        # POST: APBS workflow
        infile_name = '1fas.in'
        with open('../sample_input/1fas.in', 'r') as fin:
            apbs_infile_data = fin.read()
            response = requests.post('%s/storage/%s/1fas.in' % (APBS_URL, job_id), data=apbs_infile_data)
            assert response.status_code == 201
        with open('../sample_input/1fas.pqr', 'r') as fin:
            apbs_pqr_data = fin.read()
            response = requests.post('%s/storage/%s/1fas.pqr' % (APBS_URL, job_id), data=apbs_pqr_data)
            assert response.status_code == 201
        params = prepare_tests.prepare_workflow_v2(workflow_name='apbs', infile_name=infile_name)
        response = requests.post('%s/%s/apbs' % (workflow_url, job_id), json=params)
        assert response.status_code == 202
        json_dict = json.loads(response.content)
        assert 'accepted' in json_dict.keys()

        # GET: check status of running workflow
        # GET: continually check status of running workflow until finished
        # GET: check status of completed workflow
        common_assertions.assert_workflow_status(workflow_url, job_id, 'apbs')


        ''' Specify workflow in JSON payload '''
        # TODO: POST: PDB2PQR workflow with all details in JSON payload
        # TODO: POST: APBS workflow with all details in JSON payload

        # OPTIONS: available options within response header
        response = requests.options(job_id_url)
        assert response.status_code == 204
        assert response.headers['Access-Control-Allow-Headers'] == 'x-requested-with'
        assert response.headers['Access-Control-Allow-Methods'] == str(['GET', 'POST'])

    finally:
        # Remove contents from bucket
        requests.delete('%s/storage/%s' % (APBS_URL, job_id)) 

    pass

def test_autofill_service():
    pass