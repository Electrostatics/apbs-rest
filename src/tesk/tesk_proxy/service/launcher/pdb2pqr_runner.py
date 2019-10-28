import os, sys, time
import glob
import requests
import logging
from multiprocessing import Process
from pprint import pprint

from service import tesk_proxy_utils
from service.legacy.pdb2pqr_old_utils import redirector, setID
from service.legacy.weboptions import WebOptions, WebOptionsError

from service.legacy.src.pdb import readPDB
from service.legacy.src.aconf import (
                                            # STYLESHEET, 
                                            # WEBSITE, 
                                            # PDB2PQR_OPAL_URL,
                                            # HAVE_PDB2PQR_OPAL,
                                            INSTALLDIR,
                                            TMPDIR,
                                            MAXATOMS, 
                                            PDB2PQR_VERSION)

class JobDirectoryExistsError(Exception):
    def __init__(self, expression):
        self.expression = expression

class Runner:
    def __init__(self, form, files, storage_host, job_id=None):
        # self.starttime = None
        # self.job_id = None
        self.weboptions = None
        self.invoke_method = None
        self.cli_params = None

        self.starttime = time.time()
        if job_id is None:
            self.job_id = setID(self.starttime)
        else:
            self.job_id = job_id        

        try:
            # if 'invoke_method' in form and isinstance(form['invoke_method'], str):
            if 'invoke_method' in form :
                print('invoke_method found, value: %s' % str(form['invoke_method']) )
                if form['invoke_method'].lower() == 'cli':
                    self.invoke_method = 'cli'
                    self.cli_params = {
                        'pdb_name' : form['pdb_name'],
                        'pqr_name' : form['pqr_name'],
                        'flags' : form['flags']
                    }
                    
                elif form['invoke_method'].lower() == 'gui':
                    self.invoke_method = 'gui'
                    self.weboptions = WebOptions(form, files)
            else:
                print('invoke_method not found: %s' % str('invoke_method' in form))
                if 'invoke_method' in form:
                    print("form['invoke_method']: "+str(form['invoke_method']))
                    print(type(form['invoke_method']))
                self.invoke_method = 'gui'
                self.weboptions = WebOptions(form, files)

        except WebOptionsError as error:
            print(error)
            sys.exit(2)

    def prepare_job(self, job_id):

        
        # os.makedirs('%s%s%s' % (INSTALLDIR, TMPDIR, job_id))
        # job_id_exists = False
        # try:
        #     os.makedirs('%s%s%s' % (INSTALLDIR, TMPDIR, job_id))
        # except:
        #     job_id_exists = True
        #     pass
        # if job_id_exists:
        #     raise JobDirectoryExistsError('Job directory exists for the id %s' % job_id)
        try:
            os.makedirs('%s%s%s' % (INSTALLDIR, TMPDIR, job_id))
        except:
            pass
            
        #Some job parameters logging.
        if self.invoke_method == 'gui':
            apbsInputFile = open('%s%s%s/apbs_input' % (INSTALLDIR, TMPDIR, job_id),'w')
            apbsInputFile.write(str(self.weboptions["apbs"]))
            apbsInputFile.close()
            
            typemapInputFile = open('%s%s%s/typemap' % (INSTALLDIR, TMPDIR, job_id),'w')
            typemapInputFile.write(str(self.weboptions["typemap"]))
            typemapInputFile.close()

            # Recording CGI run information for PDB2PQR Opal
            pdb2pqrLogFile = open('%s%s%s/pdb2pqr_log' % (INSTALLDIR, TMPDIR, job_id), 'w')
            pdb2pqrLogFile.write(str(self.weboptions.getOptions())+'\n'+
                                        str(self.weboptions.ff))
                                    #  str(weboptions.ff)+'\n'+
                                    #  str(os.environ["REMOTE_ADDR"]))
            pdb2pqrLogFile.close()

        elif self.invoke_method == 'cli':
            pass

        statusfile = open('%s%s%s/pdb2pqr_status' % (INSTALLDIR, TMPDIR, job_id), 'w')
        statusfile.write('running')
        statusfile.close()


    def run_job(self, job_id, storage_host, tesk_host):
        pqr_name = None
        # print(self.weboptions.pdbfilestring)
        # pdblist, errlist = readPDB(self.weboptions.pdbfile)

        currentdir = os.getcwd()
        os.chdir("/")
        # os.setsid()
        # os.umask(0)
        os.chdir(currentdir)
        # os.close(1) # not sure if these
        # os.close(2) # two lines are necessary


        # pqrpath = '%s%s%s/%s.pqr' % (INSTALLDIR, TMPDIR, job_id, job_id)

        # orig_stdout = sys.stdout
        # orig_stderr = sys.stderr
        # sys.stdout = open('%s%s%s/pdb2pqr_stdout.txt' % (INSTALLDIR, TMPDIR, job_id), 'w')
        # sys.stderr = open('%s%s%s/pdb2pqr_stderr.txt' % (INSTALLDIR, TMPDIR, job_id), 'w')
        
        if self.invoke_method == 'gui' or self.invoke_method == 'v1':

            run_arguements = self.weboptions.getRunArguments()
            if self.weboptions.runoptions.get('ph_calc_method', '') == 'pdb2pka':
                run_arguements['ph_calc_options']['output_dir']='%s%s%s/pdb2pka_output' % (INSTALLDIR, TMPDIR, job_id)
            
            # Retrieve information about the PDB file and command line arguments
            if self.weboptions.user_did_upload:
                upload_list = ['pdb2pqr_status', 'pdb2pqr_start_time']
            else:
                if os.path.splitext(self.weboptions.pdbfilename)[1] != '.pdb':
                    self.weboptions.pdbfilename = self.weboptions.pdbfilename+'.pdb' # add pdb extension to pdbfilename
                    # Write the PDB file contents to disk
                    with open(os.path.join(INSTALLDIR, TMPDIR, job_id, self.weboptions.pdbfilename), 'w') as fout:
                        fout.write(self.weboptions.pdbfilestring)
                        upload_list = [self.weboptions.pdbfilename, 'pdb2pqr_status', 'pdb2pqr_start_time']

            self.weboptions.pqrfilename = job_id+'.pqr' # make pqr name prefix the job_id
            command_line_args = self.weboptions.getCommandLine()
            if '--summary' in command_line_args:
                command_line_args = command_line_args.replace('--summary', '')
            print(command_line_args)
            print(self.weboptions.pdbfilename)
            
            if self.weboptions.user_did_upload:
                upload_list = ['pdb2pqr_status', 'pdb2pqr_start_time']
            else:
                if os.path.splitext(self.weboptions.pdbfilename)[1] != '.pdb':
                    self.weboptions.pdbfilename = self.weboptions.pdbfilename+'.pdb' # add pdb extension to pdbfilename
                print(self.weboptions.pdbfilename)
                # Write the PDB file contents to disk
                with open(os.path.join(INSTALLDIR, TMPDIR, job_id, self.weboptions.pdbfilename), 'w') as fout:
                    fout.write(self.weboptions.pdbfilestring)
                upload_list = [self.weboptions.pdbfilename, 'pdb2pqr_status', 'pdb2pqr_start_time']

        elif self.invoke_method == 'cli' or self.invoke_method == 'v2':
            # construct command line argument string for when CLI is invoked
            command_line_list = []
            # get list of args from self.cli_params['flags']
            for name in self.cli_params['flags']:
                command_line_list.append( (name, self.cli_params['flags'][name]) )
            
            command_line_args = ''

            # append to command_line_str
            for pair in command_line_list:
                if isinstance(pair[1], bool):
                    cli_arg = '--%s' % (pair[0]) #add conditionals later to distinguish between data types
                else:
                    cli_arg = '--%s=%s' % (pair[0], str(pair[1])) #add conditionals later to distinguish between data types
                command_line_args = '%s %s' % (command_line_args, cli_arg)

            # append self.cli_params['pdb_name'] and self.cli_params['pqr_name'] to command_line_str
            pprint(self.cli_params)
            command_line_args = '%s %s %s' % (command_line_args, self.cli_params['pdb_name'], self.cli_params['pqr_name'])
            upload_list = ['pdb2pqr_status', 'pdb2pqr_start_time']

            pqr_name = self.cli_params['pqr_name']
            logging.info('pqr filename: %s' % pqr_name)


        # Write the start time to a file, before posting to TESK
        with open(os.path.join(INSTALLDIR, TMPDIR, job_id, 'pdb2pqr_start_time'), 'w') as fout:
            fout.write( str(time.time()) )

        # set the PDB2PQR status to running, write to disk, upload
        with open(os.path.join(INSTALLDIR, TMPDIR, job_id, 'pdb2pqr_status'), 'w') as fout:
            fout.write('running\n')

        tesk_proxy_utils.send_to_storage_service(storage_host, job_id, upload_list, os.path.join(INSTALLDIR, TMPDIR))

        # TESK request headers
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'
        pdb2pqr_json = tesk_proxy_utils.pdb2pqr_json_config(job_id, command_line_args, storage_host, os.path.join(INSTALLDIR, TMPDIR), pqr_name=pqr_name)


        # from pprint import pprint
        pprint(pdb2pqr_json)

        url = tesk_host + '/v1/tasks/'
        print(url)
        
        #TODO: create handler in case of non-200 response
        response = requests.post(url, headers=headers, json=pdb2pqr_json)
        
        print(response.content)
        return

    def start(self, storage_host, tesk_host):
        # Acquire job ID
        self.starttime = time.time()
        # job_id = setID(self.starttime)
        job_id = self.job_id
        # job_id = requests.get()

        # Prepare job
        self.prepare_job(job_id)

        # Run PDB2PQR in separate process
        # p = Process(target=self.run_job, args=(job_id, storage_host))
        # p.start()

        self.run_job(job_id, storage_host, tesk_host)

        # Upload initial files to storage service
        redirect = redirector(job_id, self.weboptions)
        # file_list = [
        #     'typemap',
        #     'pdb2pqr_status',
        #     'pdb2pqr_start_time',
        # ]
        # if isinstance(file_list, list):
        #     try:
        #         tesk_proxy_utils.send_to_storage_service(storage_host, job_id, file_list, os.path.join(INSTALLDIR, TMPDIR))
        #     except Exception as err:
        #         with open('storage_err', 'a+') as fin:
        #             fin.write(err)
                    
        return redirect
