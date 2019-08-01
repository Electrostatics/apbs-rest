import os, sys, time
import glob
import requests
from multiprocessing import Process

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

        self.starttime = time.time()
        if job_id is None:
            self.job_id = setID(self.starttime)
        else:
            self.job_id = job_id        

        try:
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
        apbsInputFile = open('%s%s%s/apbs_input' % (INSTALLDIR, TMPDIR, job_id),'w')
        apbsInputFile.write(str(self.weboptions["apbs"]))
        apbsInputFile.close()
        
        typemapInputFile = open('%s%s%s/typemap' % (INSTALLDIR, TMPDIR, job_id),'w')
        typemapInputFile.write(str(self.weboptions["typemap"]))
        typemapInputFile.close()

        statusfile = open('%s%s%s/pdb2pqr_status' % (INSTALLDIR, TMPDIR, job_id), 'w')
        statusfile.write('running')
        statusfile.close()
        
        # Recording CGI run information for PDB2PQR Opal
        pdb2pqrLogFile = open('%s%s%s/pdb2pqr_log' % (INSTALLDIR, TMPDIR, job_id), 'w')
        pdb2pqrLogFile.write(str(self.weboptions.getOptions())+'\n'+
                                    str(self.weboptions.ff))
                                #  str(weboptions.ff)+'\n'+
                                #  str(os.environ["REMOTE_ADDR"]))
        pdb2pqrLogFile.close()

    def run_job(self, job_id, storage_host, tesk_host):
        # print(self.weboptions.pdbfilestring)
        pdblist, errlist = readPDB(self.weboptions.pdbfile)

        currentdir = os.getcwd()
        os.chdir("/")
        # os.setsid()
        # os.umask(0)
        os.chdir(currentdir)
        # os.close(1) # not sure if these
        # os.close(2) # two lines are necessary


        pqrpath = '%s%s%s/%s.pqr' % (INSTALLDIR, TMPDIR, job_id, job_id)

        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        # sys.stdout = open('%s%s%s/pdb2pqr_stdout.txt' % (INSTALLDIR, TMPDIR, job_id), 'w')
        # sys.stderr = open('%s%s%s/pdb2pqr_stderr.txt' % (INSTALLDIR, TMPDIR, job_id), 'w')
        
        run_arguements = self.weboptions.getRunArguments()
        if self.weboptions.runoptions.get('ph_calc_method', '') == 'pdb2pka':
            run_arguements['ph_calc_options']['output_dir']='%s%s%s/pdb2pka_output' % (INSTALLDIR, TMPDIR, job_id)
        

        # Retrieve information about the PDB file and command line arguments
        # self.weboptions.pdbfilename = self.weboptions.pdbfilename+'.pdb' # add pdb extension to pdbfilename
        self.weboptions.pqrfilename = job_id+'.pqr' # make pqr name prefix the job_id
        command_line_args = self.weboptions.getCommandLine()
        if '--summary' in command_line_args:
            command_line_args = command_line_args.replace('--summary', '')
        print(command_line_args)
        print(self.weboptions.pdbfilename)

        # Write the PDB file contents to disk
        with open(os.path.join(INSTALLDIR, TMPDIR, job_id, self.weboptions.pdbfilename), 'w') as fout:
            fout.write(self.weboptions.pdbfilestring)

        # Write the start time to a file, before posting to TESK
        with open(os.path.join(INSTALLDIR, TMPDIR, job_id, 'pdb2pqr_start_time'), 'w') as fout:
            fout.write( str(time.time()) )

        # set the PDB2PQR status to running, write to disk, upload
        with open(os.path.join(INSTALLDIR, TMPDIR, job_id, 'pdb2pqr_status'), 'w') as fout:
            fout.write('running\n')
        upload_list = [self.weboptions.pdbfilename, 'pdb2pqr_status', 'pdb2pqr_start_time']
        tesk_proxy_utils.send_to_storage_service(storage_host, job_id, upload_list, os.path.join(INSTALLDIR, TMPDIR))

        # TESK request headers
        headers = {}
        headers['Content-Type'] = 'application/json'
        headers['Accept'] = 'application/json'
        pdb2pqr_json = tesk_proxy_utils.pdb2pqr_json_config(job_id, command_line_args, storage_host)


        from pprint import pprint
        pprint(pdb2pqr_json)

        url = tesk_host + '/v1/tasks/'
        print(url)
        response = requests.post(url, headers=headers, json=pdb2pqr_json)
        
        print(response.content)
        return

        exit(0)

        from service.legacy.main import runPDB2PQR
        # """
        header, lines, missedligands = runPDB2PQR(pdblist, 
                                                    self.weboptions.ff,
                                                    outname = pqrpath,
                                                    commandLine = self.weboptions.getCommandLine(),
                                                    **self.weboptions.getRunArguments())
        
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr

        endtimefile = open('%s%s%s/pdb2pqr_end_time' % (INSTALLDIR, TMPDIR, job_id), 'w')
        endtimefile.write(str(time.time()))
        endtimefile.close()

        pqrfile = open(pqrpath, "w")
        pqrfile.write(header)
        
        whitespace = self.weboptions.otheroptions['whitespace']
        for line in lines:
            # Adding whitespaces if --whitespace is in the weboptions
            if whitespace: 
                if line[0:4] == 'ATOM':
                    newline = line[0:6] + ' ' + line[6:16] + ' ' + line[16:38] + ' ' + line[38:46] + ' ' + line[46:]
                    # pqrfile.write("%s\n" % string.strip(newline))
                    pqrfile.write("%s\n" % newline.strip())
                elif line[0:6] == 'HETATM':
                    newline = line[0:6] + ' ' + line[6:16] + ' ' + line[16:38] + ' ' + line[38:46] + ' ' + line[46:]
                    # pqrfile.write("%s\n" % string.strip(newline))
                    pqrfile.write("%s\n" % newline.strip())
            else: 
                # pqrfile.write("%s\n" % string.strip(line))
                pqrfile.write("%s\n" % line.strip())
        pqrfile.close()
                
        if self.weboptions.otheroptions['apbs']:
            from service.legacy.src import inputgen
            from service.legacy.src import psize
            method = "mg-auto"
            size = psize.Psize()
            size.parseInput(pqrpath)
            size.runPsize(pqrpath)
            async = 0 # No async files here!
            myinput = inputgen.Input(pqrpath, size, method, async, potdx=True)
            myinput.printInputFiles()
            myinput.dumpPickle()
                    
        endtime = time.time() - self.starttime
        #createResults(header, input, job_id, endtime, missedligands)
        #logRun(weboptions, endtime, len(lines), weboptions.ff, os.environ["REMOTE_ADDR"])
        #printHeader("PDB2PQR Job Submission",have_opal,jobid=job_id)
        if 'ligand' in self.weboptions:
            outputligandfile = open('%s%s%s/%s.mol2' % (INSTALLDIR,TMPDIR, job_id, job_id),'w')
            outputligandfile.write(self.weboptions.ligandfilestring)
            outputligandfile.close()
        outputpdbfile = open('%s%s%s/%s.pdb' % (INSTALLDIR,TMPDIR,job_id,job_id),'w')
        outputpdbfile.write(self.weboptions.pdbfilestring)
        outputpdbfile.close()

        statusfile = open('%s%s%s/pdb2pqr_status' % (INSTALLDIR, TMPDIR, job_id), 'w')
        statusfile.write('complete\n')
        filelist = glob.glob('%s%s%s/%s*' % (INSTALLDIR, TMPDIR, job_id, job_id))
        for filename in filelist:
            statusfile.write(filename+'\n')
        statusfile.close()

        '''Upload associated APBS run files to the storage service'''
        # from . import jobutils
        jobDir = os.path.join(INSTALLDIR, TMPDIR, job_id)
        sys.stdout = open('%s/debug_forked_stdout.out' % (jobDir), 'a+')
        sys.stderr = open('%s/debug_forked_stderr.out' % (jobDir), 'a+')
        file_list = os.listdir(jobDir)
        if isinstance(file_list, list):
            try:
                tesk_proxy_utils.send_to_storage_service(storage_host, job_id, file_list, os.path.join(INSTALLDIR, TMPDIR))
            except Exception as err:
                with open('storage_err', 'a+') as fin:
                    fin.write(err)
        # sys.stdout.close()
        # sys.stderr.close()
        # """


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
