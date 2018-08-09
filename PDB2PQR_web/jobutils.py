import os
from src.aconf import *
from json import JSONEncoder

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


def get_jobstatusinfo(jobid, jobtype):
    """Returns the status and potential output files for the specified job id and type"""
    job_status = None
    job_progress = []
    job_status_path = '%s%s%s/%s_status' % (INSTALLDIR, TMPDIR, jobid, jobtype)
    if os.path.exists(job_status_path):
        '''
        If status file exists, populate job_status and job_progress
        with the status and potential output files, respectively
        '''
        fin = open(job_status_path, 'r')
        for line in fin:
            line_stripped = line.strip()
            if os.path.exists(line_stripped):
                job_progress.append(line_stripped)
            elif  len(job_progress) == 0:
                job_progress.append(line_stripped)
        fin.close()
        job_status = job_progress[0]

        '''Converts the retrieved files to URL-friendly versions'''
        for i in range(1, len(job_progress)):
            filename = job_progress[i].split('/')[-1]
            job_progress[i] = '%s%s%s/%s' % (WEBSITE, TMPDIR, jobid, filename)

    return job_status, job_progress