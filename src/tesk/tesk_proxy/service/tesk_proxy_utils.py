from __future__ import print_function
import os, sys, requests
from sys import stdout
from json import loads

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
    # stdout.write('  done\n\n')

    pass

def apbs_json_config(job_id, command_line_args, storage_host):
        apbs_json = loads( open(os.path.join(os.getcwd(), 'json_templates', 'apbs.json')).read() )
        apbs_json['name'] = apbs_json['name'].replace(b'{{job_id}}', job_id)

        json_command = apbs_json['executors'][0]['command'][2]
        json_command = json_command.replace(b'{{infile}}', command_line_args)

        wget_str = ''
        download_list = ['1a1p.pqr', 'apbsinput.in']
        for file_name in download_list:
            wget_str += 'wget %s/api/storage/%s/%s' % (storage_host, job_id, file_name)
            wget_str += ' && '
        json_command = json_command.replace(b'{{object_list}}', wget_str)

        apbs_json['executors'][0]['command'][2] = json_command
        apbs_json['executors'][0]['env']['JOB_ID'] = job_id
        apbs_json['executors'][0]['env']['STORAGE_HOST'] = storage_host

        return apbs_json

def pdb2pqr_json_config(job_id, command_line_args, storage_host):
    pdb2pqr_json = loads( open(os.path.join(os.getcwd(), 'json_templates', 'pdb2pqr.json')).read() )
    pdb2pqr_json['name'] = pdb2pqr_json['name'].replace(b'{{job_id}}', job_id)

    # Insert PDB2PQR command line arguments
    json_command = pdb2pqr_json['executors'][0]['command'][2]
    json_command = json_command.replace(b'{{args}}', command_line_args)

    arg_list = command_line_args.split()

    # Construct wget list
    download_list = [arg_list[-2]]
    wget_str = ''
    for file_name in download_list:
        wget_str += 'wget %s/api/storage/%s/%s' % (storage_host, job_id, file_name)
        wget_str += ' && '
    json_command = json_command.replace(b'{{object_list}}', wget_str)

    # Get pqr file basename, insert as upload_results.sh argument
    pqr_basename_prefix = os.path.splitext(arg_list[-1])[0]
    json_command = json_command.replace(b'{{output_basename}}', pqr_basename_prefix)

    pdb2pqr_json['executors'][0]['command'][2] = json_command
    pdb2pqr_json['executors'][0]['env']['JOB_ID'] = job_id
    pdb2pqr_json['executors'][0]['env']['STORAGE_HOST'] = storage_host

    return pdb2pqr_json