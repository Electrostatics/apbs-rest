from flask_socketio import emit, disconnect
from flask import Blueprint
from flask_socketio import SocketIO
import pprint as pp
import status_utils

status_app = Blueprint('status_app', __name__)
status_socketio = SocketIO()

@status_socketio.on('status')
def get_status(json):
    """Socket-based interface for fetching job status
    
    Given a JSON-based message containing 'jobid' with a valid ID, a JSON response is constructed with the status of the specified job.
    Message must specify which job type is desired.  Server will send disconnect message if jobid or jobtype are missing.

    For example, with a message encoded as:
        {
            'jobtype' : 'pdb2pqr', 
            'jobid'   : '15584731704'
        }

    Flask should return something like the following if the job is running:
        {
            "pdb2pqr": {
                "status": "running",
                "files": [],
                "endTime": None,
                "startTime": 1533661466.62
            },
            "jobid": "15336614662"
        }
    
    And as the following if the job is complete:
        {
            "pdb2pqr": {
                "status": "complete",
                "files": ["15336614662/15336614662-input.p", "15336614662/15336614662.in", "15336614662/15336614662.pdb", "15336614662/15336614662.pqr", "15336614662/15336614662.summary"],
                "endTime": 1533661467.76,
                "startTime": 1533661466.62
            },
            "jobid": "15336614662"
        }

    """



    def make_and_emit_status():
        '''constructs dictionary to be sent to client through socket'''
        status_response['jobid'] = job_id
        status_response[job_type] = {
            'status'    : run_state,
            'files'     : progress[1:],
            'startTime' : start_time,
            'endTime'   : end_time
        }
        emit(job_type+'_status', status_response)

    print('checking status...')

    end_states = ['complete', 'error']
    progress   = None
    run_state  = None
    start_time = None
    end_time   = None
    status_response = {}

    if json.has_key('jobid') and json.has_key('jobtype'):

        job_id = json['jobid']
        job_type = json['jobtype']

        start_time  = status_utils.get_starttime(job_id, job_type)
        end_time    = status_utils.get_endtime(job_id, job_type)
        run_state, progress = status_utils.get_jobstatus_info(job_id, job_type)
        
        make_and_emit_status()

        # If a job is still running, or isn't at a termination point, sleep until
        # job completion
        if run_state not in end_states:
            while run_state not in end_states:
                status_socketio.sleep(1)
                run_state = status_utils.get_jobstatus_state(job_id, job_type)

            print('%s - %s reached end state: %s' % (job_type, job_id, str(run_state)))
            start_time  = status_utils.get_starttime(job_id, job_type)
            end_time    = status_utils.get_endtime(job_id, job_type)
            run_state, progress = status_utils.get_jobstatus_info(job_id, job_type)

            make_and_emit_status()

        print('...status sent, terminating connection')
        emit('disconnect', 'termination')
    else:
        make_and_emit_status()
        emit('disconnect', 'missing jobid or jobtype in message')


