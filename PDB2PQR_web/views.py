from flask import render_template, redirect, request, send_from_directory
from PDB2PQR_web import app
import os
import main_cgi
import querystatus
# import pdb2pqr.main_cgi

navbar_links = {
    "navbar_home"     : "/home",
    "navbar_about"    : "http://www.poissonboltzmann.org/",
    "legacy_ucsd"     : "http://nbcr-222.ucsd.edu/pdb2pqr_2.1.1/"
}

@app.route('/', methods=["GET", "POST"])
@app.route('/home', methods=["GET", "POST"])
@app.route('/pdb2pqr', methods=["GET", "POST"])
@app.route('/apbs', methods=["GET", "POST"])
def home():
    # return render_template("index.html", navbar_home="/", navbar_about="http://www.poissonboltzmann.org/")
    return render_template("index.html", **navbar_links)

@app.route('/jobstatus', methods=["GET", "POST"])
def jobstatus():
    if request.method == 'POST':
        f = request.files
        print(request.form["PDBID"])
        redirectURL = main_cgi.mainCGI(request.form, request.files)
        # print redirectURL
        return redirect(redirectURL)
        # return("should be redirected to: "+str(redirectURL))
        # return redirect( redirectURL )

    elif request.method == 'GET':
        # print("Job Id: "+request.args['jobid'])
        return render_template( "index.html", **navbar_links)
        # return( "This should be the job status page: " + request.query_string )
        # return main_cgi.mainCGI()


@app.route('/about')
def about():
    return redirect(navbar_links["navbar_about"])

@app.route('/legacy')
def legacy():
    return redirect(navbar_links["legacy_ucsd"])

@app.route('/api/jobstatus')
def status_and_files():
    from src.aconf import *
    from json import JSONEncoder

    # if request.args['jobid'] != None:
    json_status = {}
    if request.args.has_key('jobid'):
        jobid = request.args['jobid']

        ''' Obtains status info for PDB2PQR '''
        pdb2pqr_progress = []
        pdb2pqr_status = None
        pdb2pqr_status_path = '%s%s%s/%s_status' % (INSTALLDIR,TMPDIR,jobid, 'pdb2pqr')
        if os.path.exists(pdb2pqr_status_path):
            fin = open(pdb2pqr_status_path, 'r')
            for line in fin:
                pdb2pqr_progress.append(line.strip())
            fin.close()
            pdb2pqr_status = pdb2pqr_progress[0]

            for i in range(1, len(pdb2pqr_progress)):
                filename = pdb2pqr_progress[i].split('/')[-1]
                pdb2pqr_progress[i] = '%s%s%s/%s' % (WEBSITE, TMPDIR, jobid, filename)

        ''' Obtains status info for APBS '''
        apbs_progress = []
        apbs_status = None
        apbs_status_path = '%s%s%s/%s_status' % (INSTALLDIR,TMPDIR,jobid, 'apbs')
        if os.path.exists(apbs_status_path):
            fin = open(apbs_status_path, 'r')
            for line in fin:
                apbs_progress.append(line.strip())
            fin.close()
            apbs_status = apbs_progress[0]
            for i in range(1, len(apbs_progress)):
                filename = apbs_progress[i].split('/')[-1]
                apbs_progress[i] = '%s%s%s/%s' % (WEBSITE, TMPDIR, jobid, filename)

        ''' Builds JSON response of job status '''
        json_status['jobID'] = jobid
        json_status['pdb2pqr'] = {
            'status': pdb2pqr_status,
            'files': pdb2pqr_progress[1:]
        }
        json_status['apbs'] = {
            'status': apbs_status,
            'files': apbs_progress[1:]
        }
        return JSONEncoder().encode(json_status)

    else:
        json_status['jobid'] = None
        return JSONEncoder().encode(json_status)
        # return "No job ID specified. <i>YEET</i>"

@app.route('/tmp/<jobid>/<filename>')
def job_file(jobid, filename):
    from src.aconf import *
    job_path = os.path.join(INSTALLDIR, TMPDIR, jobid)
    return send_from_directory(job_path, filename)