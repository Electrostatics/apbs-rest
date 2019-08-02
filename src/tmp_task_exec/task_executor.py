from __future__ import print_function
from flask import request, Blueprint, redirect
import os, time
# import task_utils
import executor_utils
from launcher import pdb2pqr_runner, apbs_runner

try:
    import simplejson as json
except:
    import json

tmp_executor = Blueprint('tmp_executor', __name__)

STORAGE_HOST = os.environ.get('STORAGE_HOST', 'http://localhost:5000')

@tmp_executor.route('/', methods=['GET'])
@tmp_executor.route('/check', methods=['GET'])
def is_alive():
    return '', 200

@tmp_executor.route('/api/exec/<job_id>/<task_name>', methods=['POST'])
def execute_task(job_id, task_name):
    response = None
    http_status = None

    if task_name.lower() in ['apbs', 'pdb2pqr']:
        if task_name.lower() == 'apbs':

            print("initiating APBS runner")
            if 'infile' in request.args and request.args['infile'].lower() == 'true':
                print('found infile in args')
                if request.data.has_key('filename'):
                    infile_name = request.data['filename']
                    # print(infile_name)

                    runner = apbs_runner.Runner(STORAGE_HOST, job_id=job_id, infile_name=infile_name)
                else:
                    '''CONSTRUCT SOME TYPE OF ERROR RESPONSE HERE'''
                    pass

            else:
                form = request.data
                for key in form.keys():
                    if key == 'output_scalar':
                        for option in form[key]:
                            form[option] = option
                        form.pop('output_scalar')
                    elif not isinstance(form[key], str):
                        form[key] = str(form[key])
                runner = apbs_runner.Runner(STORAGE_HOST, job_id=job_id, form=form)

            print("launching APBS runner")
            redirectURL = runner.start(STORAGE_HOST)

        elif task_name.lower() == 'pdb2pqr':
            import pprint as pp

            # form_dict = json.loads(request.data)
            # print(type(form_dict))
            form = request.data
            pp.pprint(form)

            # runner = pdb2pqr_runner.Runner(request.form, request.files, STORAGE_HOST)
            runner = pdb2pqr_runner.Runner(form, request.files, STORAGE_HOST, job_id=job_id)
            redirectURL = runner.start(STORAGE_HOST)

        '''=== DEBUG LINE FOR DEV: REMOVE IN FINAL ==='''
        if 'http://localhost:5000' in redirectURL:
            print(redirectURL)
            redirectURL = redirectURL.replace('http://localhost:5000', 'http://localhost:3000')
            print(redirectURL)
        '''==========================================='''

        # return redirect(redirectURL)

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


    return response, http_status