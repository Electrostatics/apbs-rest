from __future__ import print_function
import os, sys, logging, requests, calendar
from sys import stdout
from json import loads, dumps
from datetime import datetime
try:
    from io import StringIO
except:
    from StringIO import StringIO

from kubernetes import client, config
import yaml
import kubernetes.client
from kubernetes.client.rest import ApiException

def send_to_storage_service(storage_host, job_id, file_list, local_upload_dir):
    if sys.version_info[0] == 2:
        stdout.write('Uploading to storage container... \n')
        stdout.flush()
    elif sys.version_info[0] == 3:
        print('Uploading to storage container... ', end='')
        pass

    for f in file_list:
        # print(f)
        stdout.write('    sending %s ...\n' % f)
        # time.sleep(0.5)
        f_name = os.path.join(local_upload_dir, job_id, f)
        files = {'file_data': open(f_name, 'rb')}
        url = '%s/api/storage/%s/%s' % (storage_host, job_id, f)

        response = requests.post(url, files=files)
        print('    status code: '+str(response.status_code))
    stdout.write(u'...uploading done\n\n')
    stdout.flush()
    # stdout.write('  done\n\n')

def export_input_file_list(file_list, job_id, prefix, job_dir):
    output_name = '%s_input_files' % (prefix)
    output_name_path = '%s/%s' % (job_dir, output_name)
    fout = open(output_name_path, 'w')
    
    for name in file_list:
        fout.write('%s/%s\n' % (job_id, name))
    fout.close()
    print('Input file written to: %s' % output_name_path)

    return output_name

def apbs_extract_input_files(job_id, infile_name, storage_host):
    object_name = "%s/%s" % (job_id, infile_name)
    url = '%s/api/storage/%s?json=true' % (storage_host, object_name)
    response = requests.get(url) # TODO: check response code
    infile_text = response.json()[object_name]

    # Read only the READ section of infile, 
    # extracting out the files needed for APBS
    READ_start = False
    READ_end = False
    file_list = []
    for whole_line in StringIO(u'%s' % infile_text):
        line = whole_line.strip()
        # print(line)
        # for arg in line.split():
        #     # print(line.split())
        #     if line.startswith('#'):
        #         pass
        #     elif arg.upper() == 'READ':
        #         READ_start = True
        #     elif arg.upper() == 'END':
        #         READ_end = True
        #     elif READ_start and not READ_end:
        #         file_list.append(arg)
        #     else:
        #         pass

        #     if READ_start and READ_end:
        #         break

        if READ_start and READ_end:
            break
        
        elif not READ_start and not READ_end:
            if line.startswith('#'):
                pass
            else:
                split_line = line.split()
                if len(split_line) > 0:
                    if split_line[0].upper() == 'READ':
                        # print('ENTERING READ SECTION')
                        READ_start = True
                    elif split_line[0].upper() == 'END':
                        # print('LEAVING READ SECTION')
                        READ_end = True

        elif READ_start and not READ_end:
            if line.startswith('#'):
                pass
            else:
                split_line = line.split()
                if len(split_line) > 0:
                    if split_line[0].upper() == 'END':
                        # print('LEAVING READ SECTION')
                        READ_end = True
                    else:
                        # print('line.split()[2:]', line.split()[2:])
                        # print(split_line)
                        for arg in line.split()[2:]:
                            file_list.append(arg)

    # Slice list to only include files and nothing else in READ section
    # file_list = file_list[2:]
    return file_list

# def apbs_json_config(job_id, command_line_args, storage_host):
def apbs_json_config(job_id, infile_name, storage_host, local_upload_dir):
    # Load job template JSON string; insert job_id and storage_host into
    json_template_str = open(os.path.join(os.getcwd(), 'job_templates', 'apbs_v2.json')).read() 
    json_template_str = json_template_str.replace(b'{{job_id}}', job_id)
    json_template_str = json_template_str.replace(b'{{storage_host}}', '%s/api/storage' % storage_host)
    # json_template_str = json_template_str.replace(b'{{infile}}', command_line_args)
    json_template_str = json_template_str.replace(b'{{infile}}', infile_name)

    # Append required download files to downloader container
    # infile_name = 'apbsinput.in'
    download_list = apbs_extract_input_files(job_id, infile_name, storage_host)
    download_list = download_list + [infile_name]
    json_dict = loads(json_template_str)
    container_command = json_dict['executors'][0]['command']
    json_dict['executors'][0]['command'] = container_command + download_list

    # Export and upload list of input files
    job_dir = '%s%s' % (local_upload_dir, job_id)
    inputfile_list_name = export_input_file_list(download_list, job_id, 'apbs', job_dir)
    send_to_storage_service(storage_host, job_id, [inputfile_list_name], local_upload_dir)

    return json_dict

# def apbs_yaml_config(job_id, kube_namespace, infile_name, storage_host):
def apbs_yaml_config(job_id, kube_namespace, image_pull_policy, infile_name, storage_host, local_upload_dir):
    # Load job template JSON string; insert job_id and storage_host into
    template_name = 'apbs-volcano-template.yaml'
    job_memory_limit = os.environ.get('APBS_JOB_MEM_LIMIT', None)
    uploader_memory_limit = os.environ.get('APBS_UPLOAD_MEM_LIMIT', None)
    job_image_repo = os.environ.get('APBS_JOB_IMAGE_REPO', None)
    job_image_tag = os.environ.get('APBS_JOB_IMAGE_TAG', None)

    # uploader_cpu_request = os.environ.get('APBS_UPLOAD_CPU_REQUEST', None)
    # uploader_cpu_limit = os.environ.get('APBS_UPLOAD_CPU_LIMIT', None)

    if job_memory_limit is None:
        raise ValueError("Missing environment variable 'APBS_JOB_MEM_LIMIT'.")
    if uploader_memory_limit is None:
        raise ValueError("Missing environment variable 'APBS_UPLOAD_MEM_LIMIT'.")
    if job_image_repo is None:
        raise ValueError("Missing environment variable 'APBS_JOB_IMAGE_REPO'.")
    if job_image_tag is None:
        raise ValueError("Missing environment variable 'APBS_JOB_IMAGE_TAG'.")
    # if uploader_cpu_request is None:
    #     raise ValueError("Missing environment variable 'APBS_UPLOAD_CPU_REQUEST'.")
    # if uploader_cpu_limit is None:
    #     raise ValueError("Missing environment variable 'APBS_UPLOAD_CPU_LIMIT'.")

    job_image_name = '%s:%s' % (job_image_repo, job_image_tag)

    json_template_str = open(os.path.join(os.getcwd(), 'job_templates', template_name)).read() 
    # json_template_str = open(os.path.join(os.getcwd(), 'apbs', template_name)).read() 
    json_template_str = json_template_str.replace(b'{{job_id}}', job_id)
    json_template_str = json_template_str.replace(b'{{storage_url}}', '%s/api/storage' % storage_host)
    # json_template_str = json_template_str.replace(b'{{storage_host}}', '%s/api/storage' % storage_host)
    json_template_str = json_template_str.replace(b'{{infile}}', infile_name)
    json_template_str = json_template_str.replace(b'{{namespace}}', kube_namespace)
    json_template_str = json_template_str.replace(b'{{image_pull_policy}}', image_pull_policy) 
    json_template_str = json_template_str.replace(b'{{executor_image_name}}', job_image_name)
    json_template_str = json_template_str.replace(b'{{executor_memory_limit}}', job_memory_limit)
    json_template_str = json_template_str.replace(b'{{uploader_memory_limit}}', uploader_memory_limit)

    # Append required download files to downloader container
    # infile_name = 'apbsinput.in'
    download_list = apbs_extract_input_files(job_id, infile_name, storage_host)
    download_list = download_list + [infile_name]
    
    # append additional params to the download list through YAML
    kube_obj_dict = yaml.load(json_template_str, Loader=yaml.FullLoader)
    container_command = kube_obj_dict['spec']['tasks'][0]['template']['spec']['initContainers'][0]['command']
    kube_obj_dict['spec']['tasks'][0]['template']['spec']['initContainers'][0]['command'] = container_command + download_list

    # Export and upload list of input files
    job_dir = '%s%s' % (local_upload_dir, job_id)
    inputfile_list_name = export_input_file_list(download_list, job_id, 'apbs', job_dir)
    send_to_storage_service(storage_host, job_id, [inputfile_list_name], local_upload_dir)

    return kube_obj_dict


# def pdb2pqr_yaml_config(job_id, kube_namespace, command_line_args, storage_host, pqr_name=None):
def pdb2pqr_yaml_config(job_id, kube_namespace, image_pull_policy, command_line_args, storage_host, local_upload_dir, pqr_name=None):
    # Load job template JSON string; insert job_id and storage_host into
    # template_name = 'pdb2pqr-volcano-template.yaml'
    template_name = 'pdb2pqr-volcano-template.yaml'
    job_memory_limit = os.environ.get('PDB2PQR_JOB_MEM_LIMIT', None)
    if job_memory_limit is None:
        raise ValueError("Missing environment variable 'PDB2PQR_JOB_MEM_LIMIT'.")

    json_template_str = open(os.path.join(os.getcwd(), 'job_templates', template_name)).read()
    json_template_str = json_template_str.replace(b'{{job_id}}', job_id)
    json_template_str = json_template_str.replace(b'{{storage_url}}', '%s/api/storage' % storage_host)
    json_template_str = json_template_str.replace(b'{{namespace}}', kube_namespace)
    json_template_str = json_template_str.replace(b'{{image_pull_policy}}', image_pull_policy) 
    json_template_str = json_template_str.replace(b'{{executor_memory_limit}}', job_memory_limit)

    # Insert PDB2PQR command line arguments
    json_template_str = json_template_str.replace(b'{{command_line_args}}', command_line_args) 

    # Get pqr file basename, insert as upload_results.sh argument
    arg_list = command_line_args.split()
    pdb_filename = arg_list[-2]
    logging.info('pqr filename: %s' % pqr_name)
    logging.info('type(pqr_name): %s' % type(pqr_name))
    if isinstance(pqr_name, unicode) and len(pqr_name) > 0:
        logging.info('os.path.splitext(pqr_name)[0]: %s' % os.path.splitext(pqr_name)[0])
        json_template_str = json_template_str.replace(b'{{output_basename}}', os.path.splitext(pqr_name)[0] )
    else:
        json_template_str = json_template_str.replace(b'{{output_basename}}', job_id )

    # Extract user forcefield, user names, and ligand files; prepare download list for container
    download_list = []
    for arg in arg_list:
        if '--userff' in arg:
            userff_filename = arg.split('=')[1]
            download_list.append(userff_filename)
        elif '--usernames' in arg:
            usernames_filename = arg.split('=')[1]
            download_list.append(usernames_filename)
        elif '--ligand' in arg:
            ligand_filename = arg.split('=')[1]
            download_list.append(ligand_filename)
    
    # Construct list of files for download container
    # download_list = [pdb_filename]
    download_list.append(pdb_filename)
    kube_obj_dict = yaml.load(json_template_str, Loader=yaml.FullLoader)
    download_container_command = kube_obj_dict['spec']['tasks'][0]['template']['spec']['initContainers'][0]['command']
    kube_obj_dict['spec']['tasks'][0]['template']['spec']['initContainers'][0]['command'] = download_container_command + download_list

    # Export and upload list of input files
    job_dir = '%s%s' % (local_upload_dir, job_id)
    inputfile_list_name = export_input_file_list(download_list, job_id, 'pdb2pqr', job_dir)
    send_to_storage_service(storage_host, job_id, [inputfile_list_name], local_upload_dir)

    return kube_obj_dict

def pdb2pqr_json_config(job_id, command_line_args, storage_host, local_upload_dir, pqr_name=None):
    # Load job template JSON string; insert job_id and storage_host into
    json_template_str = open(os.path.join(os.getcwd(), 'job_templates', 'pdb2pqr_v2.json')).read()
    json_template_str = json_template_str.replace(b'{{job_id}}', job_id)
    json_template_str = json_template_str.replace(b'{{storage_host}}', '%s/api/storage' % storage_host)

    # Get pqr file basename, insert as upload_results.sh argument
    arg_list = command_line_args.split()
    pdb_filename = arg_list[-2]
    # json_template_str = json_template_str.replace(b'{{output_basename}}', os.path.splitext(pdb_filename)[0] )
    logging.info('pqr filename: %s' % pqr_name)
    logging.info('type(pqr_name): %s' % type(pqr_name))
    if isinstance(pqr_name, unicode) and len(pqr_name) > 0:
        logging.info('os.path.splitext(pqr_name)[0]: %s' % os.path.splitext(pqr_name)[0])
        json_template_str = json_template_str.replace(b'{{output_basename}}', os.path.splitext(pqr_name)[0] )
    else:
        json_template_str = json_template_str.replace(b'{{output_basename}}', job_id )

    # Extract user forcefield, user names, and ligand files; prepare download list for container
    download_list = []
    for arg in arg_list:
        if '--userff' in arg:
            userff_filename = arg.split('=')[1]
            download_list.append(userff_filename)
        elif '--usernames' in arg:
            usernames_filename = arg.split('=')[1]
            download_list.append(usernames_filename)
        elif '--ligand' in arg:
            ligand_filename = arg.split('=')[1]
            download_list.append(ligand_filename)
    

    # Insert PDB2PQR command line arguments
    json_dict = loads(json_template_str)
    json_command = json_dict['executors'][1]['command']
    json_dict['executors'][1]['command'] = json_command + arg_list

    # Construct list of files for download container
    # download_list = [pdb_filename]
    download_list.append(pdb_filename)
    container_command = json_dict['executors'][0]['command']
    json_dict['executors'][0]['command'] = container_command + download_list

    # Export and upload list of input files
    job_dir = '%s%s' % (local_upload_dir, job_id)
    inputfile_list_name = export_input_file_list(download_list, job_id, 'pdb2pqr', job_dir)
    send_to_storage_service(storage_host, job_id, [inputfile_list_name], local_upload_dir)

    return json_dict

"""
    Utility functions which interact with Kubernetes and/or Volcano
    TODO: move *_yaml_config() functions down here
"""

VOLCANO_GROUP = 'batch.volcano.sh' 
VOLCANO_VERSION = 'v1alpha1' 
VOLCANO_PLURAL = 'jobs' 
VOLCANO_PRETTY = 'true' 
VOLCANO_CONFIGURATION = None

def get_volcano_job(job_id, task_name, kube_namespace):
    VOLCANO_CONFIGURATION = kubernetes.client.Configuration()
    assert isinstance(VOLCANO_CONFIGURATION, kubernetes.client.configuration.Configuration)
    api_instance = kubernetes.client.CustomObjectsApi(kubernetes.client.ApiClient(VOLCANO_CONFIGURATION))

    if task_name == 'pdb2pqr':
        task_name = 'pdb'
    job_name = 'task-%s-%s' % (job_id, task_name)

    try:
        logging.info("Retrieving info for vcjob object '%s'", job_name)
        api_response = api_instance.get_namespaced_custom_object(VOLCANO_GROUP, VOLCANO_VERSION, kube_namespace, VOLCANO_PLURAL, job_name)
        # pprint(api_response)
    except ApiException as e:
        logging.error("Could not find vcjob object '%s'", job_name)
        logging.error("Exception when calling CustomObjectsApi->get_namespaced_custom_object: %s", e)
        if e.reason == 'Not Found' and e.status == 404:
            return {'error': True, 'reason': e.reason, 'status': e.status}
    return api_response

def get_kube_pod(pod_name, kube_namespace):
    pod_info = None
    VOLCANO_CONFIGURATION = kubernetes.client.Configuration()
    assert isinstance(VOLCANO_CONFIGURATION, kubernetes.client.configuration.Configuration)
    api_instance = kubernetes.client.CoreV1Api(kubernetes.client.ApiClient(VOLCANO_CONFIGURATION))
    try:
        pod_info = api_instance.read_namespaced_pod(pod_name, kube_namespace)
        # print( pod_info )
        # print( type(pod_info) )
    except ApiException as e:
        logging.error("Could not find pod object '%s'", pod_name)
        logging.error("Exception when calling CoreV1Api->read_namespaced_pod: %s", e)

    return pod_info

def extract_pod_container_info_list(pod_info_dict):
    status_list = []
    if pod_info_dict is not None:
        if pod_info_dict.status.init_container_statuses is not None and pod_info_dict.status.container_statuses is not None:
            for container in pod_info_dict.status.init_container_statuses + pod_info_dict.status.container_statuses:
                status_info = {}
                status_info['state_info'] = {}
                status_info['name'] = container.name

                if container.state.waiting is not None:
                    state = container.state.waiting
                    status_info['state'] = 'waiting'
                    status_info['state_info']['reason'] = state.reason
                    status_info['state_info']['message'] = state.message

                elif container.state.running is not None:
                    state = container.state.running
                    status_info['state'] = 'running'
                    status_info['state_info']['started_at'] = calendar.timegm( state.started_at.timetuple() )

                elif container.state.terminated is not None:
                    state = container.state.terminated
                    status_info['state'] = 'terminated'
                    status_info['state_info']['started_at'] = calendar.timegm( state.started_at.timetuple() )
                    status_info['state_info']['finished_at'] = calendar.timegm( state.finished_at.timetuple() )
                    status_info['state_info']['exit_code'] = state.exit_code
                    status_info['state_info']['reason'] = state.reason
                    status_info['state_info']['message'] = state.message

                # status_list.append(container)
                status_list.append(status_info)
    return status_list

# def parse_pod_status_info(status_list):
#     for status in status_list:
#         if 

def get_exit_code_from_storage(job_id, task_name, storage_host):
    url = '%s/api/storage/%s/%s_exec_exit_code.txt' % (storage_host, job_id, task_name)
    response = requests.get(url)
    if response.ok:
        data = response.content
        data = data.strip()
        return int(data)
    else:
        return None
        # raise FileNotFoundError('Could not find file for exit code')
    # pass

def parse_volcano_job_info(vcjob_info_dict, storage_host):
    assert isinstance(vcjob_info_dict, dict)
    RFC3339_format = '%Y-%m-%dT%H:%M:%SZ'
    status     = None
    start_time = None
    end_time   = None
    return_status = {}

    # tasks = vcjob_info_dict['metadata']['labels']['tasks'].split(';')[0] # splitting on ';' in case there's more tasks in future
    job_id = vcjob_info_dict['metadata']['labels']['jobid']
    tasks = vcjob_info_dict['metadata']['labels']['tasks'] # 'apbs' or 'pdb2pqr'
    vcjob_name = vcjob_info_dict['metadata']['name']

    # Get associate pod info for jobname
    vcpod_name = '%s-%s-0' % (vcjob_name, vcjob_info_dict['spec']['tasks'][0]['name'])
    namespace = vcjob_info_dict['metadata']['namespace']
    pod_info = get_kube_pod(vcpod_name, namespace)
    pod_container_list = extract_pod_container_info_list(pod_info)

    # Get start time
    start_time = vcjob_info_dict['metadata']['creationTimestamp']
    start_time = datetime.strptime(start_time, RFC3339_format) # convert from RFC3339 timestamp to datetime object
    start_time = calendar.timegm( start_time.timetuple() ) # convert datetime to num-seconds

    job_phase = vcjob_info_dict['status']['state']['phase']
    status = None
    if 'failed' in vcjob_info_dict['status']:
        # Set status
        status = 'failed'
        # Get end time
        end_time = vcjob_info_dict['status']['state']['lastTransitionTime']
        end_time = datetime.strptime(end_time, RFC3339_format) # convert from RFC3339 timestamp to datetime object
        end_time = calendar.timegm( end_time.timetuple() )
        
    elif 'succeeded' in vcjob_info_dict['status']: 
        # Set status
        exit_code = get_exit_code_from_storage(job_id, tasks, storage_host)
        if exit_code == 0: # TODO: will need to change 'tasks' once more tasks are implemented
            status = 'complete'
        elif exit_code == None:
            # raise FileNotFoundError('Could not determine exit code of %s' % tasks)
            raise OSError('Could not determine exit code of %s' % tasks)
        else:
            status = 'failed'
        
        # Get end time
        end_time = vcjob_info_dict['status']['state']['lastTransitionTime']
        end_time = datetime.strptime(end_time, RFC3339_format) # convert from RFC3339 timestamp to datetime object
        end_time = calendar.timegm( end_time.timetuple() )

    elif 'pending' in vcjob_info_dict['status'] or 'Pending' == vcjob_info_dict['status']['state']['phase']: 
        # Set status as 'pending' if first init container is 'waiting'.
        #   ^implies that no further containers would've started either
        # if pod_info is not None and pod_container_list[0]['state'] == 'waiting':
        #     status = 'pending'
        # else:
        #     status = 'running'

        if pod_info is None:
            status = 'pending'
        elif not pod_container_list:
            status = 'pending'
        elif pod_container_list and pod_container_list[0]['state'] == 'waiting':
            status = 'pending'
        else:
            status = 'running'


        
    elif 'running' in vcjob_info_dict['status']: 
        # Set status
        status = 'running'
    else:
        logging.info( dumps(vcjob_info_dict, indent=2) )

    return_status['status'] = status
    return_status['startTime'] = start_time
    return_status['endTime'] = end_time
    return_status['taskStatus'] = pod_container_list
    logging.info( dumps(return_status, indent=2) )
    return return_status
