import time, os
from src import utilities
from src.aconf import (STYLESHEET, 
                       WEBSITE, 
                       PDB2PQR_OPAL_URL,
                       HAVE_PDB2PQR_OPAL,
                       INSTALLDIR,
                       TMPDIR,
                       MAXATOMS, 
                       PDB2PQR_VERSION)

def setID(time):
    """
        Given a floating point time.time(), generate an ID.
        Use the tenths of a second to differentiate.

        Parameters
            time:  The current time.time() (float)
        Returns
            id  :  The file id (string)
    """
    strID = "%s" % time
    # period = string.find(strID, ".")
    period = strID.find(".")
    id = "%s%s" % (strID[:period], strID[(period+1):(period+2)])
    return id


def redirector(name, weboptions, jobtype=None):
    """
        Prints a page which redirects the user to querystatus.cgi and writes starting time to file
    """
    
    redirectWait = 3

    utilities.startLogFile(name, 'pdb2pqr_start_time', str(time.time()))
    
    jobtype_query = ''
    if jobtype is not None:
        jobtype_query = '&jobtype=%s' % jobtype
    
    jobid = name
    
    if weboptions is None:
        ui_url = os.getenv("UI_URL", "http://localhost:3000")
        redirectURL = "{website}jobstatus?jobid={jobid}{jobtype}".format(website=ui_url, jobid=jobid, jobtype=jobtype_query)
    else:
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
            
        redirectURL = "{website}jobstatus?jobid={jobid}{jobtype}".format(website=WEBSITE, jobid=jobid, jobtype=jobtype_query)

        #     string = """
        # <html>
        #     <head>
        #         {trackingscript}
        #         <script type="text/javascript">
        #             {trackingevents}
        #         </script>
        #         <meta http-equiv="Refresh" content="{wait}; url={redirectURL}"> 
        #         <link rel="stylesheet" href="{website}pdb2pqr.css"type="text/css">
        #     </head>
        #     <body>
        #     <center>
        #         You are being automatically redirected to a new location.<br />
        #         If your browser does not redirect you in {wait} seconds, or you do
        #         not wish to wait, <a href="{redirectURL}">click here</a></center>. 
        #     </body>
        # </html>""".format(trackingscript=utilities.getTrackingScriptString(jobid=jobid), 
        #                   trackingevents=eventsScriptString, redirectURL=redirectURL, wait=redirectWait, website=WEBSITE)
            # return string
    return redirectURL
