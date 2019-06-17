"""
    Driver for PDB2PQR

    This module takes a PDB file as input and performs optimizations
    before yielding a new PDB-style file as output.

    Ported to Python by Todd Dolinsky (todd@ccb.wustl.edu)
    Washington University in St. Louis

    Parsing utilities provided by Nathan A. Baker (Nathan.Baker@pnl.gov)
    Pacific Northwest National Laboratory

    Copyright (c) 2002-2011, Jens Erik Nielsen, University College Dublin; 
    Nathan A. Baker, Battelle Memorial Institute, Developed at the Pacific 
    Northwest National Laboratory, operated by Battelle Memorial Institute, 
    Pacific Northwest Division for the U.S. Department Energy.; 
    Paul Czodrowski & Gerhard Klebe, University of Marburg.

	All rights reserved.

	Redistribution and use in source and binary forms, with or without modification, 
	are permitted provided that the following conditions are met:

		* Redistributions of source code must retain the above copyright notice, 
		  this list of conditions and the following disclaimer.
		* Redistributions in binary form must reproduce the above copyright notice, 
		  this list of conditions and the following disclaimer in the documentation 
		  and/or other materials provided with the distribution.
        * Neither the names of University College Dublin, Battelle Memorial Institute,
          Pacific Northwest National Laboratory, US Department of Energy, or University
          of Marburg nor the names of its contributors may be used to endorse or promote
          products derived from this software without specific prior written permission.

	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
	ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
	WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
	IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
	INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
	BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
	DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
	LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
	OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED 
	OF THE POSSIBILITY OF SUCH DAMAGE.

"""

__date__  = "5 April 2010"
__author__ = "Todd Dolinsky, Nathan Baker, Jens Nielsen, Paul Czodrowski, Jan Jensen, Samir Unni, Yong Huang"

import glob
import os
import time
import re
import sys
import string
from StringIO import StringIO
#import tempfile
#from src import pdb

#from src import structures
#from src import routines
#from src import protein
#from src import server
from src.pdb import readPDB
#from src.utilities import *
#from src.structures import *
from src.definitions import Definition
#from src.forcefield import *
#from src.routines import *
from src.protein import Protein
#from src.server import *
#from src.hydrogens import *
from src import utilities
from src.server import setID, createError
from src.aconf import (STYLESHEET, 
                       WEBSITE, 
                       PDB2PQR_OPAL_URL,
                       HAVE_PDB2PQR_OPAL,
                       INSTALLDIR,
                       TMPDIR,
                       MAXATOMS, 
                       PDB2PQR_VERSION)

import traceback

__version__ = PDB2PQR_VERSION

from weboptions import WebOptions, WebOptionsError

from main import runPDB2PQR

def printHeader(pagetitle,have_opal=None,jobid=None):
    """
        Function to print html headers
    """
    if jobid:
        if have_opal:
            print "Location: querystatus.cgi?jobid=%s&typeofjob=opal\n" % (jobid)
        else:
            print "Location: querystatus.cgi?jobid=%s&typeofjob=local\n" % (jobid)

    #print "Content-type: text/html\n"
    print "<HTML>"
    print "<HEAD>"
    print "\t<TITLE>%s</TITLE>" % pagetitle
    print "\t<link rel=\"stylesheet\" href=\"%s\" type=\"text/css\">\n" % STYLESHEET
    print "</HEAD>"
    return

def redirector(name, weboptions):
    """
        Prints a page which redirects the user to querystatus.cgi and writes starting time to file
    """
    
    redirectWait = 3

    utilities.startLogFile(name, 'pdb2pqr_start_time', str(time.time()))
    
    jobid = int(name)
    
    analiticsDict = weboptions.getOptions()
    
    events = {}
    
    events['submission'] = analiticsDict['pdb']+'|'+str("localhost:5000")
    # events['submission'] = analiticsDict['pdb']+'|'+str(os.environ["REMOTE_ADDR"])
    del analiticsDict['pdb']
    
    events['titration'] = str(analiticsDict.get('ph'))
    if 'ph' in analiticsDict:
        del analiticsDict['ph']
        
    events['apbsInput'] = str(analiticsDict.get('apbs'))
    del analiticsDict['apbs']
    
    #Clean up selected extensions output
    if 'selectedExtensions' in analiticsDict:
        analiticsDict['selectedExtensions'] = ' '.join(analiticsDict['selectedExtensions'])
    
    options = ','.join(str(k)+':'+str(v) for k,v in analiticsDict.iteritems())
    events['options']=options

    eventsScriptString = ''
    for event in events:
        eventsScriptString += utilities.getEventTrackingString(category='submissionData',
                                                               action=event, 
                                                               label=events[event]) 
        
    redirectURL = "{website}jobstatus?jobid={jobid}".format(website=WEBSITE, 
                                                                                   jobid=jobid)

    string = """
<html>
    <head>
        {trackingscript}
        <script type="text/javascript">
            {trackingevents}
        </script>
        <meta http-equiv="Refresh" content="{wait}; url={redirectURL}"> 
        <link rel="stylesheet" href="{website}pdb2pqr.css"type="text/css">
    </head>
    <body>
    <center>
        You are being automatically redirected to a new location.<br />
        If your browser does not redirect you in {wait} seconds, or you do
        not wish to wait, <a href="{redirectURL}">click here</a></center>. 
    </body>
</html>""".format(trackingscript=utilities.getTrackingScriptString(jobid=jobid), 
                  trackingevents=eventsScriptString, redirectURL=redirectURL, wait=redirectWait, website=WEBSITE)
    # return string
    return redirectURL

def handleOpal(weboptions):
    '''
        Handle opal based run.
    '''
    # Opal-specific import statements
    from AppService_client import AppServiceLocator, launchJobRequest
    from AppService_types import ns0

    inputFiles = []
    
    if 'userff' in weboptions:
        ffFile = ns0.InputFileType_Def('inputFile')
        ffFile._name = weboptions.userfffilename
        ffFile._contents = weboptions.userffstring
        inputFiles.append(ffFile)
        
    if 'usernames' in weboptions:
        namesFile = ns0.InputFileType_Def('inputFile')
        namesFile._name = weboptions.usernamesfilename
        namesFile._contents = weboptions.usernamesstring
        inputFiles.append(namesFile)
        
    if 'ligand' in weboptions:
        ligandFile = ns0.InputFileType_Def('inputFile')
        ligandFile._name = weboptions.ligandfilename
        ligandFile._contents = weboptions.ligandfilestring
        inputFiles.append(ligandFile)
        
    pdbOpalFile = ns0.InputFileType_Def('inputFile')
    pdbOpalFile._name = weboptions.pdbfilename
    pdbOpalFile._contents = weboptions.pdbfilestring
    inputFiles.append(pdbOpalFile)
     
    # launch job   
    appLocator = AppServiceLocator()
    appServicePort = appLocator.getAppServicePort(PDB2PQR_OPAL_URL)
    
    req = launchJobRequest()
    req._argList = weboptions.getCommandLine()
    req._inputFile=inputFiles

    try:
        resp=appServicePort.launchJob(req)
    except Exception, e:
        printHeader("PDB2PQR Job Submission - Error")
        print "<BODY>\n<P>"
        print "There was an error with your job submission<br>"
        print "</P>"
        print "<script type=\"text/javascript\">"
        print "var gaJsHost = ((\"https:\" == document.location.protocol) ? \"https://ssl.\" : \"http://www.\");"
        print "document.write(unescape(\"%3Cscript src=\'\" + gaJsHost + \"google-analytics.com/ga.js\' type=\'text/javascript\'%3E%3C/script%3E\"));"
        print "</script>"
        print "<script type=\"text/javascript\">"
        print "try {"
        print "var pageTracker = _gat._getTracker(\"UA-11026338-3\");"
        for key in weboptions:
            print "pageTracker._trackPageview(\"/main_cgi/has_%s_%s.html\");" % (key, weboptions[key])
        print "pageTracker._trackPageview();"
        print "} catch(err) {}</script>"
        print "</BODY>"
        print "</HTML>"
        sys.exit(2)
    
    try:
        starttime = time.time()
        name = setID(starttime)
        
        #Some job parameters logging.
        os.makedirs('%s%s%s' % (INSTALLDIR, TMPDIR, name))
        apbsInputFile = open('%s%s%s/apbs_input' % (INSTALLDIR, TMPDIR, name),'w')
        apbsInputFile.write(str(weboptions["apbs"]))
        apbsInputFile.close()
        
        typemapInputFile = open('%s%s%s/typemap' % (INSTALLDIR, TMPDIR, name),'w')
        typemapInputFile.write(str(weboptions["typemap"]))
        typemapInputFile.close()
        
        pdb2pqrOpalJobIDFile = open('%s%s%s/pdb2pqr_opal_job_id' % (INSTALLDIR, TMPDIR, name), 'w')
        pdb2pqrOpalJobIDFile.write(resp._jobID)
        pdb2pqrOpalJobIDFile.close()
        
        print redirector(name, weboptions)
        
        # Recording CGI run information for PDB2PQR Opal
        pdb2pqrOpalLogFile = open('%s%s%s/pdb2pqr_log' % (INSTALLDIR, TMPDIR, name), 'w')
        pdb2pqrOpalLogFile.write(str(weboptions.getOptions())+'\n'+
                                 str(os.environ["REMOTE_ADDR"]))
        pdb2pqrOpalLogFile.close()

    except StandardError, details:
        print details
        createError(name, details)

def handleNonOpal(weboptions, storage_host):
    """
        Handle non opal run.
    """
 
    pdblist, errlist = readPDB(weboptions.pdbfile)
    
    dummydef = Definition()
    dummyprot = Protein(pdblist, dummydef)
    """
    if len(pdblist) == 0 and len(errlist) == 0:
        text = "Unable to find PDB file - Please make sure this is "
        text += "a valid PDB file ID!"
        #print "Content-type: text/html\n"
        print text
        sys.exit(2)
    elif dummyprot.numAtoms() > MAXATOMS and weboptions["opt"] == True:
        text = "<HTML><HEAD>"
        text += "<TITLE>PDB2PQR Error</title>"
        text += "<link rel=\"stylesheet\" href=\"%s\" type=\"text/css\">" % STYLESHEET
        text += "</HEAD><BODY><H2>PDB2PQR Error</H2><P>"
        text += "Due to server limits, we are currently unable to optimize "
        text += "proteins of greater than %i atoms on the server (PDB2PQR " % MAXATOMS
        text += "found %s atoms in the selected PDB file).  If you " % dummyprot.numAtoms()
        text += "want to forgo optimization please try the server again.<P>"
        text += "Otherwise you may use the standalone version of PDB2PQR that "
        text += "is available from the <a href=\"http://pdb2pqr.sourceforge.net\">"
        text += "PDB2PQR SourceForge project page</a>."
        text += "<script type=\"text/javascript\">"
        text += "var gaJsHost = ((\"https:\" == document.location.protocol) ? \"https://ssl.\" : \"http://www.\");"
        text += "document.write(unescape(\"%3Cscript src=\'\" + gaJsHost + \"google-analytics.com/ga.js\' type=\'text/javascript\'%3E%3C/script%3E\"));"
        text += "</script>"
        text += "<script type=\"text/javascript\">"
        text += "try {"
        text += "var pageTracker = _gat._getTracker(\"UA-11026338-3\");"
        for key in weboptions:
            text += "pageTracker._trackPageview(\"/main_cgi/has_%s_%s.html\");" % (key, weboptions[key])
        text += "pageTracker._trackPageview();"
        text += "} catch(err) {}</script>"
        text += "</BODY></HTML>"
        #print "Content-type: text/html\n"
        print text
        sys.exit(2)
    """    

    try:
        starttime = time.time()
        name = setID(starttime)

        #Some job parameters logging.
        os.makedirs('%s%s%s' % (INSTALLDIR, TMPDIR, name))
        apbsInputFile = open('%s%s%s/apbs_input' % (INSTALLDIR, TMPDIR, name),'w')
        apbsInputFile.write(str(weboptions["apbs"]))
        apbsInputFile.close()
        
        typemapInputFile = open('%s%s%s/typemap' % (INSTALLDIR, TMPDIR, name),'w')
        typemapInputFile.write(str(weboptions["typemap"]))
        typemapInputFile.close()

        statusfile = open('%s%s%s/pdb2pqr_status' % (INSTALLDIR, TMPDIR, name), 'w')
        statusfile.write('running')
        statusfile.close()
        
        # Recording CGI run information for PDB2PQR Opal
        pdb2pqrLogFile = open('%s%s%s/pdb2pqr_log' % (INSTALLDIR, TMPDIR, name), 'w')
        pdb2pqrLogFile.write(str(weboptions.getOptions())+'\n'+
                                 str(weboptions.ff))
                                #  str(weboptions.ff)+'\n'+
                                #  str(os.environ["REMOTE_ADDR"]))
        pdb2pqrLogFile.close()


        pid = os.fork()
        if pid:
            from PDB2PQR_web import jobutils
            redirect = redirector(name, weboptions)
            file_list = [
                'typemap',
                'pdb2pqr_status',
                'pdb2pqr_start_time',
            ]

            print('===========')
            print(weboptions.getCommandLine())
            # for i in weboptions.getRunArguments():
            #     print(i)
            print('===========')

            if isinstance(file_list, list):
                try:
                    jobutils.send_to_storage_service(storage_host, name, file_list, os.path.join(INSTALLDIR, TMPDIR))
                except Exception as err:
                    with open('storage_err', 'a+') as fin:
                        fin.write(err)
            # print redirector(name, weboptions)
            return redirect
            sys.exit()
        else:
            currentdir = os.getcwd()
            os.chdir("/")
            os.setsid()
            os.umask(0)
            os.chdir(currentdir)
            os.close(1) # not sure if these
            os.close(2) # two lines are necessary
            
            pqrpath = '%s%s%s/%s.pqr' % (INSTALLDIR, TMPDIR, name, name)
            
            orig_stdout = sys.stdout
            orig_stderr = sys.stderr
            sys.stdout = open('%s%s%s/pdb2pqr_stdout.txt' % (INSTALLDIR, TMPDIR, name), 'w')
            sys.stderr = open('%s%s%s/pdb2pqr_stderr.txt' % (INSTALLDIR, TMPDIR, name), 'w')
            
            run_arguements = weboptions.getRunArguments()
            if weboptions.runoptions.get('ph_calc_method', '') == 'pdb2pka':
                run_arguements['ph_calc_options']['output_dir']='%s%s%s/pdb2pka_output' % (INSTALLDIR, TMPDIR, name)
            
            
            header, lines, missedligands = runPDB2PQR(pdblist, 
                                                      weboptions.ff,
                                                      outname = pqrpath,
                                                      commandLine = weboptions.getCommandLine(),
                                                      **weboptions.getRunArguments())
            
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr

            endtimefile = open('%s%s%s/pdb2pqr_end_time' % (INSTALLDIR, TMPDIR, name), 'w')
            endtimefile.write(str(time.time()))
            endtimefile.close()

            pqrfile = open(pqrpath, "w")
            pqrfile.write(header)
            
            whitespace = weboptions.otheroptions['whitespace']
            for line in lines:
                # Adding whitespaces if --whitespace is in the weboptions
                if whitespace: 
                    if line[0:4] == 'ATOM':
                        newline = line[0:6] + ' ' + line[6:16] + ' ' + line[16:38] + ' ' + line[38:46] + ' ' + line[46:]
                        pqrfile.write("%s\n" % string.strip(newline))
                    elif line[0:6] == 'HETATM':
                        newline = line[0:6] + ' ' + line[6:16] + ' ' + line[16:38] + ' ' + line[38:46] + ' ' + line[46:]
                        pqrfile.write("%s\n" % string.strip(newline))
                else: 
                    pqrfile.write("%s\n" % string.strip(line))
            pqrfile.close()
                    
            if weboptions.otheroptions['apbs']:
                from src import inputgen
                from src import psize
                method = "mg-auto"
                size = psize.Psize()
                size.parseInput(pqrpath)
                size.runPsize(pqrpath)
                async = 0 # No async files here!
                myinput = inputgen.Input(pqrpath, size, method, async, potdx=True)
                myinput.printInputFiles()
                myinput.dumpPickle()
                        
            endtime = time.time() - starttime
            #createResults(header, input, name, endtime, missedligands)
            #logRun(weboptions, endtime, len(lines), weboptions.ff, os.environ["REMOTE_ADDR"])
            #printHeader("PDB2PQR Job Submission",have_opal,jobid=name)
            if 'ligand' in weboptions:
                outputligandfile = open('%s%s%s/%s.mol2' % (INSTALLDIR,TMPDIR, name, name),'w')
                outputligandfile.write(weboptions.ligandfilestring)
                outputligandfile.close()
            outputpdbfile = open('%s%s%s/%s.pdb' % (INSTALLDIR,TMPDIR,name,name),'w')
            outputpdbfile.write(weboptions.pdbfilestring)
            outputpdbfile.close()

            statusfile = open('%s%s%s/pdb2pqr_status' % (INSTALLDIR, TMPDIR, name), 'w')
            statusfile.write('complete\n')
            filelist = glob.glob('%s%s%s/%s*' % (INSTALLDIR, TMPDIR, name, name))
            for filename in filelist:
                statusfile.write(filename+'\n')
            statusfile.close()

            '''Upload associated APBS run files to the storage service'''
            from PDB2PQR_web import jobutils
            jobDir = os.path.join(INSTALLDIR, TMPDIR, name)
            sys.stdout = open('%s/debug_forked_stdout.out' % (jobDir), 'a+')
            sys.stderr = open('%s/debug_forked_stderr.out' % (jobDir), 'a+')
            file_list = os.listdir(jobDir)
            if isinstance(file_list, list):
                try:
                    jobutils.send_to_storage_service(storage_host, name, file_list, os.path.join(INSTALLDIR, TMPDIR))
                except Exception as err:
                    with open('storage_err', 'a+') as fin:
                        fin.write(err)
            sys.stdout.close()
            sys.stderr.close()

    #TODO: Better error reporting.
    #Also, get forked job to properly write error status on failure.
    except StandardError, details:
    #except StandardError as details:
        print traceback.format_exc()
        print sys.exc_info()[0]
        #print details
        createError(name, details)

def mainCGI(form, files, storage_host):
    """
        Main driver for running PDB2PQR from a web page
    """
    print "Content-type: text/html\n"
    import cgi
    import cgitb

    cgitb.enable()
    # form = cgi.FieldStorage()
    # print("Elvis was here")
    # if form.has_key('PDBID'):
    #     print("form['PDBID']: " + form["PDBID"])
    #     print("hello world")
    # print("form['PDB']: " + form["PDB"])
    
    try:
        weboptions = WebOptions(form, files)
    except WebOptionsError as error:
        print(error)
        sys.exit(2)
        
    if HAVE_PDB2PQR_OPAL:
        handleOpal(weboptions)
    else:
        queryURL = handleNonOpal(weboptions, storage_host)
        return queryURL
        
    return
    