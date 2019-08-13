from __future__ import print_function
import os, sys, requests
from sys import stdout
from json import loads
try:
    from io import StringIO
except:
    from StringIO import StringIO

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

    pass

def apbs_extract_input_files(job_id, infile_name, storage_host):
    object_name = "%s/%s" % (job_id, infile_name)
    url = '%s/api/storage/%s?json=true' % (storage_host, object_name)
    response = requests.get(url)
    infile_text = response.json()[object_name]

    # Read only the READ section of infile, 
    # extracting out the files needed for APBS
    READ_start = False
    READ_end = False
    file_list = []
    for whole_line in StringIO(u'%s' % infile_text):
        line = whole_line.strip()
        for arg in line.split():
            # print(line.split())
            if arg.upper() == 'READ':
                READ_start = True
            elif arg.upper() == 'END':
                READ_end = True
            else:
                file_list.append(arg)

            if READ_start and READ_end:
                break
        if READ_start and READ_end:
            break

    # Slice list to only include files and nothing else in READ section
    file_list = file_list[2:]
    return file_list

# def apbs_json_config(job_id, command_line_args, storage_host):
def apbs_json_config(job_id, infile_name, storage_host):
    # Load job template JSON string; insert job_id and storage_host into
    json_template_str = open(os.path.join(os.getcwd(), 'json_templates', 'apbs_v2.json')).read() 
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

    return json_dict

def pdb2pqr_json_config(job_id, command_line_args, storage_host):
    # Load job template JSON string; insert job_id and storage_host into
    json_template_str = open(os.path.join(os.getcwd(), 'json_templates', 'pdb2pqr_v2.json')).read()
    json_template_str = json_template_str.replace(b'{{job_id}}', job_id)
    json_template_str = json_template_str.replace(b'{{storage_host}}', '%s/api/storage' % storage_host)

    # Get pqr file basename, insert as upload_results.sh argument
    arg_list = command_line_args.split()
    pdb_filename = arg_list[-2]
    # json_template_str = json_template_str.replace(b'{{output_basename}}', os.path.splitext(pdb_filename)[0] )
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
            download_list.append()
    

    # Insert PDB2PQR command line arguments
    json_dict = loads(json_template_str)
    json_command = json_dict['executors'][1]['command']
    json_dict['executors'][1]['command'] = json_command + arg_list

    # Construct list of files for download container
    # download_list = [pdb_filename]
    download_list.append(pdb_filename)
    container_command = json_dict['executors'][0]['command']
    json_dict['executors'][0]['command'] = container_command + download_list

    return json_dict