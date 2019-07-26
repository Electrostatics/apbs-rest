# import string, sys, os, time, errno, shutil, tempfile, urllib, copy, pickle, glob
import os, time, errno
# import subprocess
import locale

from service.legacy.src.aconf import *
from service.legacy.src.utilities import (getTrackingScriptString, 
                                                getEventTrackingString,
                                                startLogFile,
                                                resetLogFile)

def fieldStorageToDict(form):
    """ Converts the CGI input from the web interface to a dictionary """
    apbsOptions = {'writeCheck':0}

    if form.has_key("writecharge") and form["writecharge"] != "":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeCharge'] = True
    else:
        apbsOptions['writeCharge'] = False
    
    if form.has_key("writepot") and form["writepot"] != "":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writePot'] = True
    else:
        apbsOptions['writePot'] = False

    if form.has_key("writesmol") and form["writesmol"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeSmol'] = True
    else:
        apbsOptions['writeSmol'] = False
        
    if form.has_key("asyncflag") and form["asyncflag"] == "on":
        apbsOptions['async'] = locale.atoi(form["async"])
        apbsOptions['asyncflag'] = True
    else:
        apbsOptions['asyncflag'] = False

    if form.has_key("writesspl") and form["writesspl"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeSspl'] = True
    else:
        apbsOptions['writeSspl'] = False

    if form.has_key("writevdw") and form["writevdw"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeVdw'] = True
    else:
        apbsOptions['writeVdw'] = False

    if form.has_key("writeivdw") and form["writeivdw"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeIvdw'] = True
    else:
        apbsOptions['writeIvdw'] = False

    if form.has_key("writelap") and form["writelap"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeLap'] = True
    else:
        apbsOptions['writeLap'] = False

    if form.has_key("writeedens") and form["writeedens"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeEdens'] = True
    else:
        apbsOptions['writeEdens'] = False

    if form.has_key("writendens") and form["writendens"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeNdens'] = True
    else:
        apbsOptions['writeNdens'] = False

    if form.has_key("writeqdens") and form["writeqdens"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeQdens'] = True
    else:
        apbsOptions['writeQdens'] = False

    if form.has_key("writedielx") and form["writedielx"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeDielx'] = True
    else:
        apbsOptions['writeDielx'] = False

    if form.has_key("writediely") and form["writediely"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeDiely'] = True
    else:
        apbsOptions['writeDiely'] = False

    if form.has_key("writedielz") and form["writedielz"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeDielz'] = True
    else:
        apbsOptions['writeDielz'] = False

    if form.has_key("writekappa") and form["writekappa"] == "on":
        apbsOptions['writeCheck'] += 1
        apbsOptions['writeKappa'] = True
    else:
        apbsOptions['writeKappa'] = False
    
    if apbsOptions['writeCheck'] > 4:
        print "Please select a maximum of four write statements."
        os._exit(99)

    # READ section variables
    apbsOptions['readType'] = "mol"
    apbsOptions['readFormat'] = "pqr"
    apbsOptions['pqrPath'] = ""
    apbsOptions['pqrFileName'] = form['pdb2pqrid']+'.pqr'

    #ELEC section variables
    apbsOptions['calcType'] = form["type"] 
    
    apbsOptions['ofrac'] = locale.atof(form["ofrac"])

    apbsOptions['dimeNX'] = locale.atoi(form["dimenx"])
    apbsOptions['dimeNY'] = locale.atoi(form["dimeny"])
    apbsOptions['dimeNZ'] = locale.atoi(form["dimenz"])

    apbsOptions['cglenX'] = locale.atof(form["cglenx"])
    apbsOptions['cglenY'] = locale.atof(form["cgleny"])
    apbsOptions['cglenZ'] = locale.atof(form["cglenz"])

    apbsOptions['fglenX'] = locale.atof(form["fglenx"])
    apbsOptions['fglenY'] = locale.atof(form["fgleny"])
    apbsOptions['fglenZ'] = locale.atof(form["fglenz"])

    apbsOptions['glenX'] = locale.atof(form["glenx"])
    apbsOptions['glenY'] = locale.atof(form["gleny"])
    apbsOptions['glenZ'] = locale.atof(form["glenz"])
    
    apbsOptions['pdimeNX'] = locale.atof(form["pdimex"])
    apbsOptions['pdimeNY'] = locale.atof(form["pdimey"])
    apbsOptions['pdimeNZ'] = locale.atof(form["pdimez"])

    if form["cgcent"] == "mol":
        apbsOptions['coarseGridCenterMethod'] = "molecule"
        apbsOptions['coarseGridCenterMoleculeID'] = locale.atoi(form["cgcentid"])

    elif form["cgcent"] == "coord":
        apbsOptions['coarseGridCenterMethod'] = "coordinate"
        apbsOptions['cgxCent'] = locale.atoi(form["cgxcent"])
        apbsOptions['cgyCent'] = locale.atoi(form["cgycent"])
        apbsOptions['cgzCent'] = locale.atoi(form["cgzcent"])

    if form["fgcent"] == "mol":
        apbsOptions['fineGridCenterMethod'] = "molecule"
        apbsOptions['fineGridCenterMoleculeID'] = locale.atoi(form["fgcentid"])
    elif form["fgcent"] == "coord":
        apbsOptions['fineGridCenterMethod'] = "coordinate"
        apbsOptions['fgxCent'] = locale.atoi(form["fgxcent"])
        apbsOptions['fgyCent'] = locale.atoi(form["fgycent"])
        apbsOptions['fgzCent'] = locale.atoi(form["fgzcent"])

    if form["gcent"] == "mol":
        apbsOptions['gridCenterMethod'] = "molecule"
        apbsOptions['gridCenterMoleculeID'] = locale.atoi(form["gcentid"])
    elif form["gcent"] == "coord":
        apbsOptions['gridCenterMethod'] = "coordinate"
        apbsOptions['gxCent'] = locale.atoi(form["gxcent"])
        apbsOptions['gyCent'] = locale.atoi(form["gycent"])
        apbsOptions['gzCent'] = locale.atoi(form["gzcent"])


    apbsOptions['mol'] = locale.atoi(form["mol"])
    apbsOptions['solveType'] = form["solvetype"]
    apbsOptions['boundaryConditions'] = form["bcfl"]
    apbsOptions['biomolecularDielectricConstant'] = locale.atof(form["pdie"])
    apbsOptions['dielectricSolventConstant'] = locale.atof(form["sdie"])
    apbsOptions['dielectricIonAccessibilityModel'] = form["srfm"]
    apbsOptions['biomolecularPointChargeMapMethod'] = form["chgm"]
    apbsOptions['surfaceConstructionResolution'] = locale.atof(form["sdens"])
    apbsOptions['solventRadius'] = locale.atof(form["srad"])    
    apbsOptions['surfaceDefSupportSize'] = locale.atof(form["swin"])
    apbsOptions['temperature'] = locale.atof(form["temp"])
    apbsOptions['calcEnergy'] = form["calcenergy"]
    apbsOptions['calcForce'] = form["calcforce"]

    for i in range(0,3):
        chStr = 'charge%i' % i
        concStr = 'conc%i' % i
        radStr = 'radius%i' % i
        if form[chStr] != "":
            apbsOptions[chStr] = locale.atoi(form[chStr])
        if form[concStr] != "":
            apbsOptions[concStr] = locale.atof(form[concStr])
        if form[radStr] != "":
            apbsOptions[radStr] = locale.atof(form[radStr])
    apbsOptions['writeFormat'] = form["writeformat"]
    #apbsOptions['writeStem'] = apbsOptions['pqrFileName'][:-4]
    apbsOptions['writeStem'] = form["pdb2pqrid"]


    return apbsOptions

def pqrFileCreator(apbsOptions):
    """
        Creates a pqr file, using the data from the form
    """
    print('in pqrFileCreator')
    apbsOptions['tmpDirName'] = "%s%s%s/" % (INSTALLDIR, TMPDIR, apbsOptions['writeStem'])
    print('making directory %s\n' % apbsOptions['tmpDirName'])
    try:
        os.makedirs(apbsOptions['tmpDirName'])
    except OSError, err:
        if err.errno == errno.EEXIST:
            if os.path.isdir(apbsOptions['tmpDirName']):
                # print "Error (tmp directory already exists) - please try again"
                pass
            else:
                print "Error (file exists where tmp dir should be) - please try again"
                raise
        else:
            raise

    apbsOptions['tempFile'] = "apbsinput.in"
    apbsOptions['tab'] = "    " # 4 spaces - used for writing to file
    input = open('%s/tmp/%s/%s' % (INSTALLDIR, apbsOptions['writeStem'], apbsOptions['tempFile']), 'w')
    
    print("apbsOptions['tmpDirName'] = " + apbsOptions['tmpDirName'])
    print("apbsOptions['tempFile'] = " + apbsOptions['tempFile'])
    print("apbsOptions['pqrPath'] = " + apbsOptions['pqrPath'])
    print("apbsOptions['pqrFileName'] = " + apbsOptions['pqrFileName'])

    # writing READ section to file
    input.write('read\n')
    input.write('%s%s %s %s%s' % (apbsOptions['tab'], apbsOptions['readType'], apbsOptions['readFormat'], apbsOptions['pqrPath'], apbsOptions['pqrFileName']))
    input.write('\nend\n')

    # writing ELEC section to file
    input.write('elec\n')
    input.write('%s%s\n' % (apbsOptions['tab'], apbsOptions['calcType']))
    if apbsOptions['calcType']!="fe-manual":
        input.write('%sdime %d %d %d\n' % (apbsOptions['tab'], apbsOptions['dimeNX'], apbsOptions['dimeNY'], apbsOptions['dimeNZ']))
    if apbsOptions['calcType'] == "mg-para":
        input.write('%spdime %d %d %d\n' % (apbsOptions['tab'], apbsOptions['pdimeNX'], apbsOptions['pdimeNY'], apbsOptions['pdimeNZ']))
        input.write('%sofrac %g\n' % (apbsOptions['tab'], apbsOptions['ofrac']))
        if apbsOptions['asyncflag']:
            input.write('%sasync %d\n' % (apbsOptions['tab'], apbsOptions['async']))

    if apbsOptions['calcType'] == "mg-manual":
        input.write('%sglen %g %g %g\n' % (apbsOptions['tab'], apbsOptions['glenX'], apbsOptions['glenY'], apbsOptions['glenZ']))
    if apbsOptions['calcType'] in ['mg-auto','mg-para','mg-dummy']:
        input.write('%scglen %g %g %g\n' % (apbsOptions['tab'], apbsOptions['cglenX'], apbsOptions['cglenY'], apbsOptions['cglenZ']))
    if apbsOptions['calcType'] in ['mg-auto','mg-para']:
        input.write('%sfglen %g %g %g\n' % (apbsOptions['tab'], apbsOptions['fglenX'], apbsOptions['fglenY'], apbsOptions['fglenZ']))

        if apbsOptions['coarseGridCenterMethod']=='molecule':
            input.write('%scgcent mol %d\n' % (apbsOptions['tab'], apbsOptions['coarseGridCenterMoleculeID'] ))
        elif apbsOptions['coarseGridCenterMethod']=='coordinate':
            input.write('%scgcent %d %d %d\n' % (apbsOptions['tab'], apbsOptions['cgxCent'], apbsOptions['cgyCent'], apbsOptions['cgzCent']))

        if apbsOptions['fineGridCenterMethod']=='molecule':
            input.write('%sfgcent mol %d\n' % (apbsOptions['tab'], apbsOptions['fineGridCenterMoleculeID']))
        elif apbsOptions['fineGridCenterMethod']=='coordinate':
            input.write('%sfgcent %d %d %d\n' % (apbsOptions['tab'], apbsOptions['fgxCent'], apbsOptions['fgyCent'], apbsOptions['fgzCent']))

    if apbsOptions['calcType'] in ['mg-manual','mg-dummy']:
        if apbsOptions['gridCenterMethod']=='molecule':
            input.write('%sgcent mol %d\n' % (apbsOptions['tab'], apbsOptions['gridCenterMoleculeID'] ))
        elif apbsOptions['gridCenterMethod']=='coordinate':
            input.write('%sgcent %d %d %d\n' % (apbsOptions['tab'], apbsOptions['gxCent'], apbsOptions['gyCent'], apbsOptions['gzCent']))

    input.write('%smol %d\n' % (apbsOptions['tab'], apbsOptions['mol']))
    input.write('%s%s\n' % (apbsOptions['tab'], apbsOptions['solveType']))
    input.write('%sbcfl %s\n' % (apbsOptions['tab'], apbsOptions['boundaryConditions']))
    input.write('%spdie %g\n' % (apbsOptions['tab'], apbsOptions['biomolecularDielectricConstant']))
    input.write('%ssdie %g\n' % (apbsOptions['tab'], apbsOptions['dielectricSolventConstant']))
    input.write('%ssrfm %s\n' % (apbsOptions['tab'], apbsOptions['dielectricIonAccessibilityModel']))
    input.write('%schgm %s\n' % (apbsOptions['tab'], apbsOptions['biomolecularPointChargeMapMethod']))
    input.write('%ssdens %g\n' % (apbsOptions['tab'], apbsOptions['surfaceConstructionResolution']))
    input.write('%ssrad %g\n' % (apbsOptions['tab'], apbsOptions['solventRadius']))
    input.write('%sswin %g\n' % (apbsOptions['tab'], apbsOptions['surfaceDefSupportSize']))
    input.write('%stemp %g\n' % (apbsOptions['tab'], apbsOptions['temperature']))
    input.write('%scalcenergy %s\n' % (apbsOptions['tab'], apbsOptions['calcEnergy']))
    input.write('%scalcforce %s\n' % (apbsOptions['tab'], apbsOptions['calcForce']))
    for i in range(0,3):
        chStr = 'charge%i' % i
        concStr = 'conc%i' % i
        radStr = 'radius%i' % i
        if apbsOptions.has_key(chStr) and apbsOptions.has_key(concStr) and apbsOptions.has_key(radStr):
            #ion charge {charge} conc {conc} radius {radius}
            input.write('%sion charge %d conc %g radius %g\n' % (apbsOptions['tab'], 
                                                                 apbsOptions[chStr], 
                                                                 apbsOptions[concStr], 
                                                                 apbsOptions[radStr]))

    if apbsOptions['writeCharge']:
        input.write('%swrite charge %s %s-charge\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))
    
    if apbsOptions['writePot']:
        input.write('%swrite pot %s %s-pot\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeSmol']:
        input.write('%swrite smol %s %s-smol\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeSspl']:
        input.write('%swrite sspl %s %s-sspl\n' % (apbsOptions['tab'], apbsOptions['writeFormat'],  apbsOptions['writeStem']))

    if apbsOptions['writeVdw']:
        input.write('%swrite vdw %s %s-vdw\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeIvdw']:
        input.write('%swrite ivdw %s %s-ivdw\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeLap']:
        input.write('%swrite lap %s %s-lap\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeEdens']:
        input.write('%swrite edens %s %s-edens\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeNdens']:
        input.write('%swrite ndens %s %s-ndens\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeQdens']:
        input.write('%swrite qdens %s %s-qdens\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeDielx']:
        input.write('%swrite dielx %s %s-dielx\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeDiely']:
        input.write('%swrite diely %s %s-diely\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeDielz']:
        input.write('%swrite dielz %s %s-dielz\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    if apbsOptions['writeKappa']:
        input.write('%swrite kappa %s %s-kappa\n' % (apbsOptions['tab'], apbsOptions['writeFormat'], apbsOptions['writeStem']))

    input.write('end\n')
    input.write('quit')
    input.close()

def redirector(logTime):
    # if (str(logTime) != "False") and (str(logTime) != "notenoughmem"):
    #     startLogFile(logTime, 'apbs_start_time', str(time.time()))
    #     resetLogFile(logTime, 'apbs_end_time')
#        starttimefile = open('%s%s%s/apbs_start_time' % (INSTALLDIR, TMPDIR, logTime), 'w')
#        starttimefile.write(str(time.time()))
#        starttimefile.close()
        
    redirectWait = 3
    
    redirectURL = "{website}jobstatus?jobid={jobid}".format(website=WEBSITE, 
                                                                                jobid=logTime)

#     string = """
# <html> 
#     <head>
#         {trackingscript}
# 		<link rel="stylesheet" href="css/foundation.css">
#         <script type="text/javascript">
#             {trackingevents}
#         </script>
#         <link rel="stylesheet" href="@website@pdb2pqr.css" type="text/css">
#         <meta http-equiv="refresh" content="{wait};url={redirectURL}"/>
#     </head>
#     <body>
#         <center> You are being automatically redirected to a new location.<br/>
#         If your browser does not redirect you in {wait} seconds, or you do
#         not wish to wait, <a href="{redirectURL}">click here</a> </center>. 
#     </body>
# </html>""".format(trackingscript=getTrackingScriptString(jobid=logTime),
#                   trackingevents = getEventTrackingString(category='apbs',
#                                                           action='submission', 
#                                                           label=str(os.environ["REMOTE_ADDR"])),
#                   redirectURL=redirectURL, wait=redirectWait)
    
    # return string
    return redirectURL
