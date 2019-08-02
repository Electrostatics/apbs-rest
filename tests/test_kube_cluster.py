from os import getenv
from time import sleep
from pprint import pprint
from requests import get, post
from dotenv import load_dotenv
try:
    from simplejson import loads
except:
    from json import loads

load_dotenv()

UI_HOST         = getenv('UI_HOST', default='')
ID_HOST         = getenv('ID_HOST', default='')
TASK_HOST       = getenv('TASK_HOST', default='')
EXEC_HOST       = getenv('EXEC_HOST', default='')
STORAGE_HOST    = getenv('STORAGE_HOST', default='')
WORKFLOW_HOST   = getenv('WORKFLOW_HOST', default='')

class EnvironmentValueError(ValueError):
    def __init__(self, expression):
        self.expression = 'Missing environment variable %s' % expression
        # self.message = 

def check_environment_vars():
    if UI_HOST == '': raise EnvironmentValueError('UI_HOST')
    if ID_HOST == '': raise EnvironmentValueError('ID_HOST')
    if TASK_HOST == '': raise EnvironmentValueError('TASK_HOST')
    if EXEC_HOST == '': raise EnvironmentValueError('EXEC_HOST')
    if STORAGE_HOST == '': raise EnvironmentValueError('STORAGE_HOST')
    if WORKFLOW_HOST == '': raise EnvironmentValueError('WORKFLOW_HOST')
    # raise ValueError()


def get_job_id():
    response = get('%s/id/' % ID_HOST)
    job_id = response.json()['job_id']
    return job_id

def post_to_storage(job_id, file_name):
    with open(file_name, 'r') as fin:
        name = file_name.split('/')[-1]
        files = {'file_data': fin }
        response = post('%s/storage/%s/%s' % (STORAGE_HOST, job_id, name), files=files)
        # pprint(response.content)
    
    # post()
    if response.status_code == 201:
        print('uploaded')
    else:
        print('error: %d' % response.status_code)
        exit(1)
    pass

def get_from_storage(job_id, file_name):
    pass

def submit_task(job_id, task_name, task_params=None, task_files=None, use_infile=None):
    if use_infile is True:
        response = post('%s/task/%s/%s?infile=%s' % (TASK_HOST, job_id, task_name, str(use_infile)), json=task_params)
    else:
        response = post('%s/task/%s/%s' % (TASK_HOST, job_id, task_name), json=task_params)

    return response
    # pass

def get_task_status(job_id, task_name, wait=False):
    # raise NotImplementedError
    response = get('%s/task/%s/%s?wait=%s' % (TASK_HOST, job_id, task_name, wait) )
    return response

def monitor_task_status(job_id, task_name, wait=False):
    file_names = []

    if wait == True:
        # Long-poll server to wait until task is complete
        response = get_task_status(job_id, task_name, wait=True)
        print(response.status_code)
        print(response.content)
        status = loads(response.content)
        if status[task_name]['status'] == 'complete':
            status = loads(response.content)
            file_names = status[task_name]['files']
    else:
        # Request status once-per-second until task is complete
        while(True):
            sleep(1)
            print('.', end='', flush=True)
            response = get_task_status(job_id, task_name)
            status = loads(response.content)

            if status[task_name]['status'] == 'complete':
                sleep(1)
                response = get_task_status(job_id, task_name)
                status = loads(response.content)

                file_names = status[task_name]['files']
                # pprint(status)
                break


    print()    
    return status[task_name]['status'], file_names


def submit_workflow(job_id, workflow_str, workflow_params=None, task_files=None, use_infile=None):
    if use_infile is True:
        response = post('%s/workflow/%s?infile=%s' % (WORKFLOW_HOST, job_id, str(use_infile)), json=workflow_params)
    else:
        request_json = {
            'workflow': workflow_str,
            'form': workflow_params
        }
        response = post('%s/workflow/%s' % (WORKFLOW_HOST, job_id), json=request_json)
    return response

def get_workflow_task_status(job_id, task_name, wait=False):
    response = get('%s/workflow/%s/%s?wait=%s' % (WORKFLOW_HOST, job_id, task_name, wait) )
    return response

def monitor_workflow_status(job_id, task_name, wait=False):
    file_names = []

    if wait == True:
        # Long-poll server to wait until task is complete
        # response = get_task_status(job_id, task_name, wait=True)
        response = get_workflow_task_status(job_id, task_name, wait=True)
        status = loads(response.content)
        if status[task_name]['status'] == 'complete':
            status = loads(response.content)
            file_names = status[task_name]['files']
    else:
        # Request status once-per-second until task is complete
        while(True):
            sleep(1)
            print('.', end='', flush=True)
            # response = get_task_status(job_id, task_name)
            response = get_workflow_task_status(job_id, task_name)
            status = loads(response.content)

            if status[task_name]['status'] == 'complete':
                sleep(1)
                # response = get_task_status(job_id, task_name)
                response = get_workflow_task_status(job_id, task_name)
                status = loads(response.content)

                file_names = status[task_name]['files']
                # pprint(status)
                break


    print()    
    return status[task_name]['status'], file_names


# Tests Workflow Submitter service with PDB2PQR
def start_pdb2pqr_workflow(pdb_id=None):
    print('------PDB2PQR Workflow Submit------')

    if pdb_id is None:
        pdb_id = '1a1p'

    print('  getting job ID', end='', flush=True)
    job_id = get_job_id()
    print('... %s' % job_id)
    
    # workflow_str = ['pdb2pqr']
    # workflow_str = ['pdb2pqr', 'apbs']
    workflow_str = 'pdb2pqr'

    task_params = {
        "DEBUMP"        : "atomsnotclose",
        "FF"            : "parse",
        "FFOUT"         : "internal",
        "INPUT"         : "makeapbsin",
        "OPT"           : "optimizeHnetwork",
        "PDBID"         : pdb_id,
        "PDBSOURCE"     : "ID",
        "PH"            : "7.0",
        "PKACALCMETHOD" : "propka"
    }

    task_params = {
        "DEBUMP"        : "atomsnotclose",
        "FF"            : "parse",
        "FFOUT"         : "internal",
        "INPUT"         : "makeapbsin",
        "OPT"           : "optimizeHnetwork",
        # "PDBID"         : "1abf",
        "PDBID"         : "1a1p",
        # "PDBID"         : pdb_id,
        "PDBSOURCE"     : "ID",
        "PH"            : "7.0",
        "PKACALCMETHOD" : "propka"
    }
    # task_params = [{
    #     "DEBUMP"        : "atomsnotclose",
    #     "FF"            : "parse",
    #     "FFOUT"         : "internal",
    #     "INPUT"         : "makeapbsin",
    #     "OPT"           : "optimizeHnetwork",
    #     # "PDBID"         : "1abf",
    #     "PDBID"         : "1a1p",
    #     # "PDBID"         : pdb_id,
    #     "PDBSOURCE"     : "ID",
    #     "PH"            : "7.0",
    #     "PKACALCMETHOD" : "propka"
    # },
    # {   
    #     u'bcfl': u'sdh',
    #     u'calcenergy': u'total',
    #     u'calcforce': u'no',
    #     u'cgcent': u'mol',
    #     u'cgcentid': 1,
    #     u'cglenx': 42.6292,
    #     u'cgleny': 33.078599999999994,
    #     u'cglenz': 25.117499999999996,
    #     u'charge0': u'',
    #     u'charge1': u'',
    #     u'charge2': u'',
    #     u'chgm': u'spl2',
    #     u'conc0': u'',
    #     u'conc1': u'',
    #     u'conc2': u'',
    #     u'dimenx': 97,
    #     u'dimeny': 65,
    #     u'dimenz': 65,
    #     u'fgcent': u'mol',
    #     u'fgcentid': 1,
    #     u'fglenx': 42.6292,
    #     u'fgleny': 33.078599999999994,
    #     u'fglenz': 25.117499999999996,
    #     u'gcent': u'molecule',
    #     u'glenx': 42.6292,
    #     u'gleny': 33.078599999999994,
    #     u'glenz': 25.117499999999996,
    #     u'hiddencheck': u'local',
    #     u'mol': u'1',
    #     u'ofrac': 0.1,
    #     u'output_scalar': [   u'writepot'],
    #     u'pdb2pqrid': job_id,
    #     u'pdie': 2,
    #     u'pdimex': 1,
    #     u'pdimey': 1,
    #     u'pdimez': 1,
    #     u'radius0': u'',
    #     u'radius1': u'',
    #     u'radius2': u'',
    #     u'sdens': 10,
    #     u'sdie': 78.54,
    #     u'solvetype': u'lpbe',
    #     u'srad': 1.4,
    #     u'srfm': u'smol',
    #     u'swin': 0.3,
    #     u'temp': 298.15,
    #     u'type': u'mg-auto',
    #     u'writeformat': u'dx'
    # }]    

    print('  submitting workflow parmaeters ')
    r = submit_workflow(job_id, workflow_str, workflow_params=task_params)
    # pprint(r)
    
    print('  obtaining workflow task status')
    # # status = get_task_status(job_id, task_name)
    task_name = workflow_str
    status = get_workflow_task_status(job_id, task_name)
    # status = get_task_status(job_id, task_name)

    print('  monitoring workflow status', end='', flush=True)
    status, file_names = monitor_workflow_status(job_id, task_name)
    # status, file_names = monitor_task_status(job_id, task_name)

    print('  task done; printing output file names\n')
    pprint(file_names, indent=2)

    print('-----------------------------------')


# Tests Task Submitter service with PDB2PQR
def start_pdb2pqr_task(pdb_id=None):
    print('------PDB2PQR Task Submit------')

    if pdb_id is None:
        pdb_id = '1a1p'

    print('  getting job ID', end='', flush=True)
    job_id = get_job_id()
    print('... %s' % job_id)


    task_name = 'pdb2pqr'
    task_params = {
        "DEBUMP"        : "atomsnotclose",
        "FF"            : "parse",
        "FFOUT"         : "internal",
        "INPUT"         : "makeapbsin",
        "OPT"           : "optimizeHnetwork",
        # "PDBID"         : "1abf",
        # "PDBID"         : "1a1p",
        "PDBID"         : pdb_id,
        "PDBSOURCE"     : "ID",
        "PH"            : "7.0",
        "PKACALCMETHOD" : "propka"
    }

    # print('  sending task to run')
    print('  sending task to run  ', end='')
    r = submit_task(job_id, task_name, task_params=task_params)
    print(r.status_code)
    # pprint(r)
    
    print('  obtaining task status')
    status = get_task_status(job_id, task_name)

    print('  monitoring task status', end='', flush=True)
    status, file_names = monitor_task_status(job_id, task_name)

    print('  task done\n')
    print('  Output Files:')
    pprint(file_names, indent=2)

    print('-------------------------------')

# Tests Task Submitter service with APBS
def start_apbs_task(job_id=None):
    print('--------APBS Task Submit--------')


    print('  getting job ID', end='', flush=True)
    if job_id is None:
        job_id = get_job_id()
    print('... %s' % job_id)

    task_name = 'apbs'
    in_file_name = 'apbs_upload/sample.in'
    pqr_file_name = 'apbs_upload/sample.pqr'
    
    print('  uploading sample.pqr to storage...', end='', flush=True)
    post_to_storage(job_id, pqr_file_name)
    print('  uploading sample.in to storage...', end='')
    post_to_storage(job_id, in_file_name)
    # print('  uploading apbsinput.in to storage...', end='')
    # post_to_storage(job_id, 'apbsinput.in')

    task_params = {   
        u'bcfl': u'sdh',
        u'calcenergy': u'total',
        u'calcforce': u'no',
        u'cgcent': u'mol',
        u'cgcentid': 1,
        u'cglenx': 42.6292,
        u'cgleny': 33.078599999999994,
        u'cglenz': 25.117499999999996,
        u'charge0': u'',
        u'charge1': u'',
        u'charge2': u'',
        u'chgm': u'spl2',
        u'conc0': u'',
        u'conc1': u'',
        u'conc2': u'',
        u'dimenx': 97,
        u'dimeny': 65,
        u'dimenz': 65,
        u'fgcent': u'mol',
        u'fgcentid': 1,
        u'fglenx': 42.6292,
        u'fgleny': 33.078599999999994,
        u'fglenz': 25.117499999999996,
        u'gcent': u'molecule',
        u'glenx': 42.6292,
        u'gleny': 33.078599999999994,
        u'glenz': 25.117499999999996,
        u'hiddencheck': u'local',
        u'mol': u'1',
        u'ofrac': 0.1,
        u'output_scalar': [   u'writepot'],
        # u'pdb2pqrid': u'15614178303',
        u'pdb2pqrid': job_id,
        u'pdie': 2,
        u'pdimex': 1,
        u'pdimey': 1,
        u'pdimez': 1,
        u'radius0': u'',
        u'radius1': u'',
        u'radius2': u'',
        u'sdens': 10,
        u'sdie': 78.54,
        u'solvetype': u'lpbe',
        u'srad': 1.4,
        u'srfm': u'smol',
        u'swin': 0.3,
        u'temp': 298.15,
        u'type': u'mg-auto',
        u'writeformat': u'dx'
    }

    task_params = {
        'filename': in_file_name.split('/')[1]
    }

    print('  sending task to run')
    r = submit_task(job_id, task_name, task_params=task_params)
    r = submit_task(job_id, task_name, task_params=task_params, use_infile=True)
    # pprint(r)
    
    print('  obtaining task status')
    status = get_task_status(job_id, task_name)

    print('  monitoring task status', end='', flush=True)
    status, file_names = monitor_task_status(job_id, task_name, wait=True)

    print('  task done\n')
    print('  Output Files:')
    pprint(file_names, indent=2)

    print('--------------------------------')

if __name__ == "__main__":
    #TODO: write this as a proper unit test script

    check_environment_vars()

    '''Run sample PDB2PQR job'''

    # start_pdb2pqr_task()
    # start_pdb2pqr_task(pdb_id='1hhj')

    # start_pdb2pqr_workflow(pdb_id='1hhj')
    start_pdb2pqr_workflow(pdb_id='1a1p')
    # start_pdb2pqr_task(pdb_id='1a1p')

    start_apbs_task()

    # get job ID
    # job_id = get_job_id()
    # print(job_id)

    # upload related files to storage service

    # send task
    task_name = ''

    # every 1 second
        # sleep
        # request task status
        # if task complete
            # request file names for job
            # break

    # download files to 'tmp' subdirectory
    
