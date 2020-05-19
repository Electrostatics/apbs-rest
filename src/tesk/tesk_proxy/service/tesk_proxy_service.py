from __future__ import print_function
from flask import request, Blueprint
from kubernetes import config
from launcher import pdb2pqr_runner, apbs_runner
from legacy.weboptions import WebOptionsError
from tesk_proxy_utils import get_volcano_job, parse_volcano_job_info
import os, sys, traceback, logging, json
tesk_proxy = Blueprint('tesk_proxy', __name__)

PDB2PQR_BUILD_PATH = os.environ.get('PDB2PQR_BUILD_PATH')
STORAGE_HOST = os.environ.get('STORAGE_HOST', 'http://localhost:5001')
TESK_HOST = os.environ.get('TESK_HOST', 'http://localhost:5001')
IMAGE_PULL_POLICY = os.environ.get('IMAGE_PULL_POLICY', 'Always')

GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', None)
if GA_TRACKING_ID == '': GA_TRACKING_ID = None
GA_JOBID_INDEX = os.environ.get('GA_JOBID_INDEX', None)
if GA_JOBID_INDEX == '': GA_JOBID_INDEX = None

# Bail if GA_TRACKING_ID is set but GA_JOBID_INDEX is not
if GA_TRACKING_ID is not None and GA_JOBID_INDEX is None:
    raise ValueError("GA_TRACKING_ID is set in environment but not GA_JOBID_INDEX. GA_JOBID_INDEX must be an integer.")

try:
    config.load_incluster_config()
except:
    config.load_kube_config()

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
        #TODO: Get task status from scheduling service (Volcano.sh)
        response = {}
        http_status = None
        volcano_namespace = os.environ.get('VOLCANO_NAMESPACE')
        try:
            vcjob_info = get_volcano_job(job_id, task_name, volcano_namespace)
            if 'status' in vcjob_info and vcjob_info['status'] == 404:
                # If job not found, return 404
                http_status = 404
                response['error'] = vcjob_info['reason']
                response['message'] = "Could not find instance of task '%s' for jobid '%s'" % (task_name, job_id)
                logging.info("Task '%s->%s' could not be found. Status: %s", job_id, task_name, json.dumps(vcjob_info['status'], indent=2))
            else:
                response = parse_volcano_job_info(vcjob_info, STORAGE_HOST)
                http_status = 200

        except Exception as err:
            response = {}
            response['message'] = None
            response['error'] = ('Internal error while processing request. '
                                'If error persists, please report through usual channels (email, issues, etc.)')
            http_status = 500
            logging.error(traceback.format_exc())
            # raise

    elif request.method == 'POST':
        '''
            Handler for using the TESK service.
        '''
        if task_name.lower() in ['apbs', 'pdb2pqr']:
            response = {
                'message': "Task type '%s' accepted. Beginning execution" % (task_name),
            }

            if task_name == 'apbs':
                # TODO: wrap in try/except; set response/http_code when initializing apbs_runner.Runner()
                try:
                    if 'infile' in request.args.to_dict() and request.args['infile'].lower() == 'true':
                        infile_name = request.json['filename']
                        if infile_name is None:
                            raise apbs_runner.MissingFilesError('No APBS input file specified.')

                        runner = apbs_runner.Runner(STORAGE_HOST, job_id=job_id, infile_name=infile_name)
                        redirectURL = runner.start(STORAGE_HOST, TESK_HOST, IMAGE_PULL_POLICY, GA_TRACKING_ID, GA_JOBID_INDEX)
                        
                        # Update response with URL to monitor on a browser
                        response['jobURL'] = redirectURL
                        
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
                        redirectURL = runner.start(STORAGE_HOST, TESK_HOST, IMAGE_PULL_POLICY, GA_TRACKING_ID, GA_JOBID_INDEX)

                        # Update response with URL to monitor on a browser
                        response['jobURL'] = redirectURL
                        http_status = 202
                
                # except FileNotFoundError as err:
                except apbs_runner.MissingFilesError as err:
                    logging.error('%s: %s', type(err).__name__, err) # # Print error to log
                    response['message'] = None
                    response['error'] = str(err)
                    response['missing_files'] = err.missing_files
                    http_status = 400

                    # print traceback for debugging
                    logging.error(traceback.format_exc()) # # Print error to log

                except Exception as err:
                    logging.error('%s: %s', type(err).__name__, err) # Print error to log
                    response['message'] = None
                    response['error'] = ('Internal error while processing request. '
                                         'If error persists, please report through usual channels (email, issues, etc.)')
                    http_status = 500

                    # print traceback for debugging
                    logging.error(traceback.format_exc()) # Print error to log

            elif task_name == 'pdb2pqr':
                try:
                    form = request.json
                    runner = pdb2pqr_runner.Runner(form, request.files, STORAGE_HOST, job_id=job_id)
                    redirectURL = runner.start(STORAGE_HOST, TESK_HOST, IMAGE_PULL_POLICY, GA_TRACKING_ID, GA_JOBID_INDEX)

                    # Update response with URL to monitor on a browser
                    response['jobURL'] = redirectURL
                    http_status = 202

                except WebOptionsError as err:
                    logging.error('JOB_ID--%s TASK_NAME--%s: %s', job_id, task_name, str(err))
                    response.pop('message')
                    response['error'] = str(err)
                    if err.bad_weboption is not None:
                        response['name'] = err.bad_weboption
                    http_status = 400

                except Exception as err:
                    logging.error('%s: %s', type(err).__name__, err) # Print error to log
                    response['message'] = None
                    response['error'] = ('Internal error while processing request. '
                                         'If error persists, please report through usual channels (email, issues, etc.)')
                    http_status = 500

                    # print traceback for debugging
                    logging.error(traceback.format_exc()) # Print error to log


            # response = {
            #     'message': "Task type '%s' accepted. Beginning execution" % (task_name),
            #     'jobURL': redirectURL
            # }
            # http_status = 202

        else:
            response = {
                'error': "task type '%s' does not exist or is not implemented" % (task_name)
            }
            http_status = 404
            
    # import pprint as pp
    # pp.pprint(response)

    sys.stdout.flush()
    return response, http_status