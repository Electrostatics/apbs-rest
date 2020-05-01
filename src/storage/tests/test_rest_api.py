""" Tests for rest api for storage service"""
import logging
import tarfile
from pathlib import Path
from time import time, sleep

import filecmp
import os
import subprocess
import uuid
from random import randint

import requests
import pytest

FLASK_HOST = "http://localhost:5001"
STORAGE_ENDPOINT = FLASK_HOST + "/api/storage"

# RESPONSE CODES
DELETE_OK = 204


def generate_big_random_bin_file(filename, size):
    """
    generate big binary file with the specified size in megabytes
    :param filename: the filename
    :param size: the size in megabytes
    :return:void

    note: adapted from
    https://www.bswen.com/2018/04/python-How-to-generate-random-large-file-using-python.html
    """

    with open('%s' % filename, 'wb') as fp:
        fp.write(os.urandom(size * 1024 * 1024))


def generate_big_sparse_file(filename, size):
    """
    generate sparse binary file with the specified size in megabytes
    :param filename: the filename
    :param size: the size in megabytes
    :return:void

    note: adapted from
    https://www.bswen.com/2018/04/python-How-to-generate-random-large-file-using-python.html
    """
    size = size * 1024 * 1024
    f = open(filename, "wb")
    f.seek(randint(1, int(size / 2)))
    tag = uuid.uuid4()
    f.write(tag.bytes)
    f.seek(size - 1)
    tag = uuid.uuid4()
    f.write(tag.bytes)
    f.close()
    pass


@pytest.fixture(scope="module")
def services():
    """
    setup/teardown for storage rest services
    """
    logging.info("Bringing up services via docker-compose")

    try:
        subprocess.check_call(["docker-compose", "build"])
        subprocess.check_call(["docker-compose", "up", "-d"])
        if not flask_ready_check():
            raise IOError('Failed to bring up Flask service')
        yield
    finally:
        logging.info("stopping services")
        subprocess.check_call(["docker-compose", "down"])


@pytest.fixture(scope="module")
def test_data(tmpdir_factory):
    """
    create data files for testing
    """
    logging.info("creating data files")

    # list of files sizes to generate
    sizes = (100, 200, 300)

    files = []
    for size in sizes:
        filename = F"file{size}"
        filepath = tmpdir_factory.mktemp("data") / filename
        generate_big_sparse_file(filepath, size)
        files.append(Path(filepath))

    return files


def flask_ready_check(timeout=500, poll=5):
    """
    check readiness of flask server

    Args:
        timeout: max wait time in seconds
        poll: polling time interval in seconds

    Returns:
        True if ready False otherwise


    """

    flask_ready = False

    t_start = time()
    while (time()-t_start) < timeout:
        try:
            r = requests.request("GET", FLASK_HOST)
            if r.status_code == 200:
                logging.info(F"FLASK server is ready, "
                             F"took {round(time()-t_start,1)} seconds")
                flask_ready = True
                break
        except requests.exceptions.ConnectionError:
            sleep(poll)

    return flask_ready


def test_flask_server(services):
    """
    test if flask server is alive
    """

    r = requests.request("GET", FLASK_HOST)
    assert r.status_code == 200


def test_upload(services, test_data, tmp_path):
    """
    test different end points in storage service
    """
    test_files = test_data

    job_id = 12345

    # test post operation
    for filepath in test_files:
        filename = filepath.name
        url = F'{STORAGE_ENDPOINT}/{job_id}/{filename}'
        files = {'file_data': filepath.open('rb')}
        r = requests.post(url, files=files)
        assert r.status_code == 201

    # test get operation
    for filepath in test_files:
        filename = filepath.name
        url = F'{STORAGE_ENDPOINT}/{job_id}/{filename}'
        r = requests.get(url)
        download_path = tmp_path / filename
        assert r.status_code == 200
        with download_path.open('wb') as f:
            f.write(r.content)

        assert filecmp.cmp(download_path, filepath)

    # test get operation on archive
    url = F'{STORAGE_ENDPOINT}/{job_id}'
    r = requests.get(url)
    download_dir = tmp_path / "downloaded"
    download_dir.mkdir()
    download_path = download_dir / "test.tgz"
    assert r.status_code == 200
    with download_path.open('wb') as f:
        f.write(r.content)

    with tarfile.open(download_path) as tf:
        tf.extractall(download_dir)  # specify which folder to extract to

    for filepath in test_files:
        filename = filepath.name
        assert filecmp.cmp(download_dir / filename, filepath)

    # test deletion
    url = F'{STORAGE_ENDPOINT}/{job_id}'
    r = requests.delete(url)

    assert r.status_code == DELETE_OK

