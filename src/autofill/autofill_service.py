from flask import request, make_response, Blueprint
from werkzeug.utils import secure_filename
from legacy import apbs_cgi
from legacy.src import psize, inputgen
from legacy.src.aconf import INSTALLDIR, TMPDIR
import os, sys, json, requests
import autofill_utils

STORAGE_HOST = os.environ.get('STORAGE_HOST', 'http://localhost:5001')

autofill_app = Blueprint('autofill_app', __name__)

@autofill_app.route('/', methods=['GET'])
@autofill_app.route('/check', methods=['GET'])
def is_alive():
    return '', 200

@autofill_app.route('/api/autofill/<job_id>/<job_type>', methods=['GET'])
def send_autofill_info(job_id, job_type):
    json_response_dict = {}
    json_response_dict['dummy'] = 'fetch succeeded'
    # print('job_id:   '+job_id)
    # print('job_type: '+job_type)

    if job_type == 'apbs' and job_id:
        response_id = autofill_utils.get_new_id() # id num so frontend knows to refill fields

        # json_response_dict = apbs_cgi.unpickleVars(job_id)

        # object_name = job_id/job_id.json
        # requests get job_id.json
        # load contents[object_name] into json_response_dict
        object_name = '%s/%s-input.json' % (job_id, job_id)
        r = requests.get('%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name))
        input_data = r.json()[object_name]
        json_response_dict = json.loads(input_data)
        
        json_response_dict['response_id'] = response_id
        # print(type(json_response_dict))
        # print(type(json_response_dict['dime']))
        # print(len(json_response_dict.keys()))

    ''' Prepare response to API request '''
    # response = make_response(JSONEncoder().encode(json_response_dict))
    response = make_response(json.dumps(json_response_dict))
    response.headers['Content-Type'] = 'application/json'
    # request_origin_url = request.referrer.split('?')[0]
    # if request_origin_url in ORIGIN_WHITELIST:
    #     cleared_domain = request_origin_url[:request_origin_url.index('/apbs')]
    #     response.headers['Access-Control-Allow-Origin'] = cleared_domain

    return json_response_dict

@autofill_app.route('/api/autofill/upload/<job_id>/<job_type>', methods=['POST', 'OPTIONS'])
def parse_upload(job_id, job_type):
    EXTENSION_WHITELIST = set(['pqr'])
    json_response = {}
    http_status_response = None
    # workflow_app.config['UPLOAD_FOLDER'] = os.path.join(INSTALLDIR, TMPDIR)
    upload_folder = os.path.join(INSTALLDIR, TMPDIR)

    if request.method == 'POST':
        # print(dict(request.files).keys())
        print(request)
        try:
            print(request.files.keys())

            if job_type == 'apbs':
                files = request.files['file']
                if files:
                    filename = secure_filename(files.filename)
                    # filename = 
                    mime_type = files.content_type

                    if files and autofill_utils.allowed_file(files.filename, EXTENSION_WHITELIST):
                        print("passed whitelist")
                        new_job_id = autofill_utils.get_new_id()  
                        tmp_dir_path = os.path.join(INSTALLDIR, TMPDIR)
                        job_dir_path = os.path.join(tmp_dir_path, new_job_id)
                        upload_path  = os.path.join(job_dir_path, '%s.pqr' % (new_job_id) )
                        if not os.path.exists(job_dir_path):
                            print("passed does_exists()")
                            os.makedirs(job_dir_path)
                            files.save(upload_path)

                            # Lifted from main_cgi.py APBS handler, line 626
                            method = "mg-auto"
                            size = psize.Psize()
                            size.parseInput(upload_path)
                            size.runPsize(upload_path)
                            async = 0 # No async files here!
                            myinput = inputgen.Input(upload_path, size, method, async, potdx=True)
                            myinput.printInputFiles()
                            # myinput.dumpPickle()

                            apbsOptions_dict = autofill_utils.inputgenToJSON(myinput, new_job_id)
                            input_json_name = '%s/%s-input.json' % (job_dir_path, new_job_id)
                            json.dump(apbsOptions_dict, open(input_json_name, 'w'))
                            # return autofill(new_job_id, 'apbs')
                            
                            autofill_utils.send_to_storage_service( STORAGE_HOST, new_job_id, 
                                [   new_job_id+'.pqr',
                                    new_job_id+'.in',
                                    new_job_id+'-input.json',
                                ], upload_folder )
                                # ], app.config['UPLOAD_FOLDER'] )

                            json_response = {
                                'upload_status': 'Success',
                                'job_id': new_job_id,
                            }
                            http_status_response = 201

                            # json_response = apbs_cgi.unpickleVars(new_job_id)
                    else:
                        raise Exception('File must be a PQR file')

        except Exception as e:
            # json_response = 'failed: %s' % (e)
            print(e)
            json_response = '%s' % (e)
            http_status_response = 500

    ''' Prepare response to API request '''
    response = make_response(json.dumps(json_response))
    # response.headers['Content-Type'] = 'application/json'
    if request.method == 'OPTIONS':
        # response = json_response
        # json_response = 'this is OPTIONS'
        # print('this is OPTIONS')
        # print(response)
        response = autofill_utils.get_request_options(response, 'POST')
        # response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
        # response.headers['Access-Control-Allow-Methods'] = 'POST'
        http_status_response = 204
        
    # if request.referrer:
    #     # Add origin header to response if origin is in whitelist
    #     request_origin_url = request.referrer.split('?')[0]
    #     if request_origin_url in ORIGIN_WHITELIST:
    #         print(request_origin_url)
    #         cleared_domain = request_origin_url[:request_origin_url.index('/apbs')]
    #         response.headers['Access-Control-Allow-Origin'] = cleared_domain

    return response, http_status_response