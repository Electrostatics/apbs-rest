import json, pytest
from task.service import task_utils

# CONFIG = json.load(open('tests/config_vars.json', 'r'))

@pytest.fixture(scope="module")
def start_minio():
    pass

class TestTaskUtils:

    def test_get_starttime(self):
        pass

    def test_get_endtime(self):
        pass
    
    def test_get_input_files(self):
        pass
    
    def test_get_output_files(self):
        pass

    def test_get_jobstatus_state(self):
        pass
    
    def test_get_jobstatus_info(self):
        pass
