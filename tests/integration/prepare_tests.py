def prepare_task_v1(task_name: str, pdb_id: str='1a1p', infile_name: str='apbsinput.in'):
    task_params = {}

    if task_name == 'pdb2pqr':
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
    elif task_name == 'apbs':
        task_params = {
        'filename': infile_name
        }


    # if use_infile is True:
    #     response = post('%s/task/%s/%s?infile=%s' % (TASK_HOST, job_id, task_name, str(use_infile)), json=task_params)

    return task_params

def prepare_task_v2(task_name: str, pdb_name: str):
    pass

def prepare_workflow_v1():
    pass

def prepare_workflow_v2(workflow_name: str=None, pdb_id: str='1a1p', infile_name: str='apbsinput.in'):
    workflow_params = {}
    if workflow_name == 'pdb2pqr':
        pass
    elif workflow_name == 'apbs':
        workflow_params = {
            'form': {
                'filename': infile_name
            }
        }
    else:
        # workflow specified within JSON; prepare accordingly
        pass

    return workflow_params