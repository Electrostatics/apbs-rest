import time
import os, json, tarfile, requests
import pytest, docker
from multiprocessing import Process
from minio import Minio
# from task.service import task_utils

CONFIG = json.load(open('tests/config_vars.json', 'r'))

MINIO_PORT        = CONFIG["MINIO_PORT"]
MINIO_ACCESS_KEY  = CONFIG["MINIO_ACCESS_KEY"]
MINIO_SECRET_KEY  = CONFIG["MINIO_SECRET_KEY"]
MINIO_JOB_BUCKET  = CONFIG["MINIO_JOB_BUCKET"]
MINIO_IMAGE_TAG   = CONFIG["MINIO_IMAGE_TAG"]
STORAGE_IMAGE_NAME= CONFIG["STORAGE_IMAGE_NAME"]
STORAGE_IMAGE_TAG = CONFIG["STORAGE_IMAGE_TAG"]
STORAGE_PORT      = CONFIG["STORAGE_PORT"]
JOB_ID = 'pytest'

os.environ['STORAGE_HOST'] = 'http://localhost:%s' % STORAGE_PORT
os.environ['STORAGE_URL'] = 'http://localhost:%s/api/storage' % STORAGE_PORT

from task.service import task_utils

# @pytest.fixture(scope="module")
@pytest.fixture(scope="module", autouse=True)
def start_storage_service(request):
    # Start MinIO and Storage Service docker containers
    bucket_name = 'jobs'
    minio_name = 'test_task_utils-minio'
    minio_host = 'localhost:%s' % MINIO_PORT
    storage_name = 'test_task_utils-storage'
    storage_host = 'localhost:%s' % STORAGE_PORT

    # os.environ['STORAGE_HOST'] = storage_host

    # global STORAGE_HOST
    # global STORAGE_URL
    # STORAGE_HOST = 'http://%s' % storage_host
    # STORAGE_URL = 'http://%s/api/storage' % STORAGE_HOST
    # print(STORAGE_HOST)
    # print(STORAGE_URL)

    docker_client = docker.from_env()
    minio_container = docker_client.containers.run(
                                'minio/minio:%s' % MINIO_IMAGE_TAG, 
                                'server /data',
                                name=minio_name,
                                ports={
                                    '9000/tcp':MINIO_PORT,
                                    '5001/tcp':STORAGE_PORT,
                                },
                                detach=True,
                                environment={
                                    'MINIO_ACCESS_KEY': MINIO_ACCESS_KEY,
                                    'MINIO_SECRET_KEY': MINIO_SECRET_KEY,
                                }
                            )
    storage_container = docker_client.containers.run(
                                '%s:%s' % (STORAGE_IMAGE_NAME, STORAGE_IMAGE_TAG), 
                                name=storage_name,
                                network="container:%s" % minio_name,
                                detach=True,
                                environment={
                                    'MINIO_ACCESS_KEY': MINIO_ACCESS_KEY,
                                    'MINIO_SECRET_KEY': MINIO_SECRET_KEY,
                                }
                            )

    minio_client = Minio( minio_host,
                          access_key=MINIO_ACCESS_KEY,
                          secret_key=MINIO_SECRET_KEY,
                          secure=False )

    # Create test job bucket
    minio_client.make_bucket(bucket_name)

    # Perform a ready check
    is_storage_ready = False
    while not is_storage_ready:
        try:
            response = requests.get('http://%s/' % storage_host)
            if response.status_code == 200:
                is_storage_ready = True
        except Exception:
            retry_timer = 1 # second(s)
            print('Storage service is not ready yet! Waiting %d second(s)' % retry_timer)
            time.sleep(retry_timer)

    # Method to run after all tests
    def remove_test_containers():

        storage_container.stop()
        minio_container.stop()
        
        storage_container.wait()
        minio_container.wait()
        
        storage_container.remove()
        minio_container.remove()

        docker_client.close()

    # Define as finalizer
    request.addfinalizer(remove_test_containers)

    # Upload sample tar data to storage
    tar = tarfile.open('tests/sample_job_data.tar')
    for member in tar.getmembers():
        tfin = tar.extractfile(member)
        if tfin is not None:
            post_url = 'http://%s/api/storage/%s/%s' % (storage_host, JOB_ID, member.name)
            response = requests.post(post_url, data=tfin.read())
        else:
            raise TypeError

class TestTaskUtils:

    def test_get_starttime(self, start_storage_service):
        task_name = 'pdb2pqr'
        starttime = task_utils.get_starttime(JOB_ID, task_name)
        assert starttime != None

    def test_get_endtime(self, start_storage_service):
        task_name = 'pdb2pqr'
        endtime = task_utils.get_endtime(JOB_ID, task_name)
        assert endtime != None
    
    def test_get_input_files(self, start_storage_service):
        task_name = 'pdb2pqr'
        input_files = task_utils.get_input_files(JOB_ID, task_name)
        assert len(input_files) > 0
    
    def test_get_output_files(self, start_storage_service):
        task_name = 'pdb2pqr'
        output_files = task_utils.get_output_files(JOB_ID, task_name)
        assert len(output_files) > 0

    def test_get_jobstatus_state(self, start_storage_service):
        task_name = 'pdb2pqr'
        job_status = task_utils.get_jobstatus_state(JOB_ID, task_name)
        assert job_status == 'complete'
    
    def test_get_jobstatus_info(self, start_storage_service):
        task_name = 'pdb2pqr'
        job_status, file_names = task_utils.get_jobstatus_info(JOB_ID, task_name)
        assert isinstance(job_status, str)
        assert isinstance(file_names, list)
        assert job_status == 'complete'
        assert len(file_names) == 8
