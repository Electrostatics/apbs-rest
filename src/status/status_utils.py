from __future__ import print_function
import os, time, sys
from sys import stdout

from json import JSONEncoder
from flask import make_response
import requests

pdb2pqr_build_path = os.getcwd().split('/')[:-2]
pdb2pqr_build_path.append('pdb2pqr_build')
sys.path.append( '/'+ os.path.join(*pdb2pqr_build_path) )
from src.aconf import *

def get_starttime(jobid, jobtype):
    """Returns the start time for the specified job id and type"""
    starttime = None
    jobtime_path = '%s%s%s/%s_start_time' % (INSTALLDIR, TMPDIR, jobid, jobtype)
    if os.path.exists(jobtime_path):
        fin = open(jobtime_path)
        starttime = float(fin.readline())
    return starttime


def get_endtime(jobid, jobtype):
    """Returns the end time for the specified job id and type"""
    endtime = None
    jobtime_path = '%s%s%s/%s_end_time' % (INSTALLDIR, TMPDIR, jobid, jobtype)
    if os.path.exists(jobtime_path):
        fin = open(jobtime_path)
        endtime = float(fin.readline())
    return endtime

def get_request_options(response, methods_array):
    # response = make_response
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    response.headers['Access-Control-Allow-Methods'] = methods_array
    return response

def get_jobstatus_state(jobid, jobtype):
    job_status = None
    job_status_path = '%s%s%s/%s_status' % (INSTALLDIR, TMPDIR, jobid, jobtype)
    if os.path.exists(job_status_path):
        with open(job_status_path) as fin:
            job_status = fin.readline().strip()
    return job_status


def get_jobstatus_info(jobid, jobtype):
    """Returns the status and potential output files for the specified job id and type"""
    job_status = None
    job_progress = []
    job_status_path = '%s%s%s/%s_status' % (INSTALLDIR, TMPDIR, jobid, jobtype)
    if os.path.exists(job_status_path):
        # If status file exists, populate job_status and job_progress
        # with the status and potential output files, respectively
        with open(job_status_path, 'r') as fin:
            job_status = fin.readline().strip()
            for line in fin:
                line_stripped = line.strip()
                if os.path.exists(line_stripped):
                    job_progress.append(line_stripped)
                elif  len(job_progress) == 0:
                    job_progress.append(line_stripped)

        # Converts the retrieved files to URL-friendly versions
        for i in range(1, len(job_progress)):
            filename = job_progress[i].split('/')[-1]
            job_progress[i] = '%s/%s' % (jobid, filename)
    
    return job_status, job_progress
