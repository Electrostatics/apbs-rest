from __future__ import print_function
from flask import request, Blueprint
from launcher import pdb2pqr_runner, apbs_runner
import os, sys

tesk_proxy = Blueprint('tesk_proxy', __name__)

PDB2PQR_BUILD_PATH = os.environ.get('PDB2PQR_BUILD_PATH')
STORAGE_HOST = os.environ.get('STORAGE_HOST', 'http://localhost:5001')
TESK_HOST = os.environ.get('TESK_HOST', 'http://localhost:5001')

if PDB2PQR_BUILD_PATH is not None:
    sys.path.append(PDB2PQR_BUILD_PATH)

@tesk_proxy.route('/', methods=['GET'])
@tesk_proxy.route('/check/', methods=['GET'])
def liveness():
    """Probes server to check if alive"""
    return '', 200

@tesk_proxy.route('/api/tesk/<job_id>/<task_name>', methods=['GET', 'POST'])
def submit_tesk_action(job_id, task_name):
    response = None
    http_status = None

    if request.method == 'GET':
        #TODO: Get task status from execution service (TESK/Batch)
        pass
    elif request.method == 'POST':
        '''
            Handler for using the TESK service.
        '''
        if task_name.lower() in ['apbs', 'pdb2pqr']:
            if task_name == 'apbs':
                # TODO: wrap in try/except; set response/http_code when
                #   initializing apbs_runner.Runner()
                if 'infile' in request.args.to_dict() and request.args['infile'].lower() == 'true':
                    infile_name = request.json['filename']
                    runner = apbs_runner.Runner(STORAGE_HOST, job_id=job_id, infile_name=infile_name)
                    redirectURL = runner.start(STORAGE_HOST, TESK_HOST)
                else:
                    form = request.json
                    for key in form.keys():
                        # unravels output parameters from form
                        if key == 'output_scalar':
                            for option in form[key]:
                                form[option] = option
                            form.pop('output_scalar')
                        elif not isinstance(form[key], str):
                            form[key] = str(form[key])

                    runner = apbs_runner.Runner(STORAGE_HOST, job_id=job_id, form=form)
                    redirectURL = runner.start(STORAGE_HOST, TESK_HOST)

            elif task_name == 'pdb2pqr':
                # TODO: wrap in try/except; except WebOptionsError as err, 
                #   print err, set response and http_status
                form = request.json
                runner = pdb2pqr_runner.Runner(form, request.files, STORAGE_HOST, job_id=job_id)
                redirectURL = runner.start(STORAGE_HOST, TESK_HOST)



            response = {
                'message': "Task type '%s' accepted. Beginning execution" % (task_name),
                'jobURL': redirectURL
            }
            http_status = 202

        else:
            response = {
                'error': "task type '%s' does not exist or is not implemented" % (task_name)
            }
            http_status = 404
            
    # import pprint as pp
    # pp.pprint(response)

    sys.stdout.flush()
    return response, http_status