from __future__ import print_function
import requests, time, sys, os, locale
from os import getenv
from json import loads, dumps
from flask import request
from werkzeug.utils import secure_filename

def handle_pdb2pqr_upload(upload_file, job_id, storage_host):
    if upload_file:
        file_name = secure_filename(upload_file.filename)
        if allowed_file(file_name, ['pdb', 'dat','names', 'mol2']):
            pdb_stream = upload_file.stream
            files = {'file_data': pdb_stream}
            url = '%s/api/storage/%s/%s' % (storage_host, job_id, file_name)
            r = requests.post(url, files=files)
            if r.status_code < 200 or r.status_code > 299:
                return False
    else:
        return False

    return True

def allowed_file(filename, valid_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in valid_extensions

def get_request_options(response, methods_array):
    # response = make_response
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    response.headers['Access-Control-Allow-Methods'] = methods_array
    return response

def get_new_id():
    """Returns a unique identifier string"""
    new_id = None
    try:
        response = requests.get('%s/api/uid' % getenv('ID_HOST'))
        new_id = loads(response.content)['job_id']
    except:
        new_id = str(time.time())
        new_id = new_id.replace('.','')
        
    return new_id

def send_to_storage_service(storage_host, job_id, file_list, local_upload_dir):
    if sys.version_info[0] == 2:
        sys.stdout.write('Uploading to storage container... \n')
        sys.stdout.flush()
    elif sys.version_info[0] == 3:
        print('Uploading to storage container... ', end='', flush=True)
        pass

    successful_upload = []
    for f in file_list:
        # print(f)
        sys.stdout.write('    sending %s ...\n' % f)
        # time.sleep(0.5)
        f_name = os.path.join(local_upload_dir, job_id, f)
        files = {'file_data': open(f_name, 'rb')}
        url = '%s/api/storage/%s/%s' % (storage_host, job_id, f)

        response = requests.post(url, files=files)
        print('    status code: '+str(response.status_code))

        if response.status_code >= 200 and response.status_code < 300:
            successful_upload.append(True)
        else:
            successful_upload.append(False)
            
        
    sys.stdout.write(u'...uploading done\n\n')
    # stdout.write('  done\n\n')
    
    return successful_upload


def inputgenToJSON(inputObj, job_id):
    myElec = inputObj.elecs[0]

    apbsOptions = {}
    apbsOptions['pqrname'] = job_id+'.pqr'
    apbsOptions['pdbID'] = inputObj.pqrname[:-4]
    
    if myElec.cgcent[0:3] == "mol":
        apbsOptions['coarseGridCenterMethod'] = "molecule"
        apbsOptions['coarseGridCenterMoleculeID'] = locale.atoi(myElec.cgcent[4:])
    else:
        apbsOptions['coarseGridCenterMethod'] = "coordinate"
        apbsOptions['coarseGridCenter'] = myElec.cgcent

    if myElec.fgcent[0:3] == "mol":
        apbsOptions['fineGridCenterMethod'] = "molecule"
        apbsOptions['fineGridCenterMoleculeID'] = locale.atoi(myElec.fgcent[4:])
    else:
        apbsOptions['fineGridCenterMethod'] = "coordinate"
        apbsOptions['fineGridCenter'] = myElec.fgcent

    if myElec.gcent[0:3] == "mol":
        apbsOptions['gridCenterMethod'] = "molecule"
        apbsOptions['gridCenterMoleculeID'] = locale.atoi(myElec.gcent[4:])
    else:
        apbsOptions['gridCenterMethod'] = "coordinate"
        apbsOptions['gridCenter'] = myElec.gcent


    if myElec.lpbe == 1:
        apbsOptions['solveType'] = 'linearized'
    elif myElec.npbe == 1:
        apbsOptions['solveType'] = 'nonlinearized'

    #TODO: Currently this is not used.
    if len(myElec.ion) == 0:
        apbsOptions['mobileIonSpecies[0]'] = None
    else:
        apbsOptions['mobileIonSpecies[1]'] = myElec.ion

    if len(myElec.write) <= 1:
        apbsOptions['format'] = 'dx'
    else:
        apbsOptions['format'] = myElec.write[1]

    apbsOptions['calculationType'] = myElec.method
    apbsOptions['dime'] = myElec.dime
    apbsOptions['pdime'] = myElec.pdime
    apbsOptions['async'] = myElec.async
    apbsOptions['asyncflag'] = myElec.asyncflag
    apbsOptions['nlev'] = myElec.nlev
    apbsOptions['glen'] = myElec.glen
    apbsOptions['coarseGridLength'] = myElec.cglen
    apbsOptions['fineGridLength'] = myElec.fglen
    apbsOptions['molecule'] = myElec.mol
    apbsOptions['boundaryConditions'] = myElec.bcfl
    apbsOptions['biomolecularDielectricConstant'] = myElec.pdie
    apbsOptions['dielectricSolventConstant'] = myElec.sdie
    apbsOptions['biomolecularPointChargeMapMethod'] = myElec.chgm
    apbsOptions['surfaceConstructionResolution'] = myElec.sdens
    apbsOptions['dielectricIonAccessibilityModel'] = myElec.srfm
    apbsOptions['solventRadius'] = myElec.srad
    apbsOptions['surfaceDefSupportSize'] = myElec.swin
    apbsOptions['temperature'] = myElec.temp
    apbsOptions['calculationEnergy'] = myElec.calcenergy
    apbsOptions['calculationForce'] = myElec.calcforce
    apbsOptions['processorMeshOverlap'] = myElec.ofrac
    apbsOptions['writeBiomolecularChargeDistribution'] = False
    apbsOptions['writeElectrostaticPotential'] = True
    apbsOptions['writeMolecularSurfaceSolventAccessibility'] = False
    apbsOptions['writeSplineBasedSolventAccessibility'] = False
    apbsOptions['writeVanDerWaalsSolventAccessibility'] = False
    apbsOptions['writeInflatedVanDerWaalsIonAccessibility'] = False
    apbsOptions['writePotentialLaplacian'] = False
    apbsOptions['writeEnergyDensity'] = False
    apbsOptions['writeMobileIonNumberDensity'] = False
    apbsOptions['writeMobileChargeDensity'] = False
    apbsOptions['writeDielectricMapShift'] = [False,False,False]
    apbsOptions['writeIonAccessibilityKappaMap'] = False

    return apbsOptions

"""
Functions lifted from apbs-pdb2pqr repo
"""

# from apbs-pdb2pqr/pdb2pqr/src/utilities.py
def getPQRBaseFileName(filename):
    root, ext = os.path.splitext(filename)
    if ext.lower() == '.pqr':
        return root
    return filename
