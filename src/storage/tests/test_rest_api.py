#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This is the module."""

# !/usr/bin/python
# -*- coding: utf-8 -*-
"""This is the module."""
import filecmp
import os
import subprocess
import uuid
from random import randint

import requests
from time import sleep

import pytest

FLASK_HOST = "http://localhost:5001"
STORAGE_ENDPOINT = FLASK_HOST + "/api/storage"


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


def gen_big_file(filename, size):
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
def setup():
    """
    setup/teardown for storage rest service
    """
    print("entered setup")

    try:
        subprocess.check_call(["docker-compose", "build"])
        subprocess.check_call(["docker-compose", "up", "-d"])
        sleep(2)
        yield
    finally:
        print("\n cleaning up")
        subprocess.check_call(["docker-compose", "down"])


def test_flask_server(setup):
    r = requests.request("GET", FLASK_HOST)

    assert r.status_code == 200

#
# def test_upload():
#
#     job_id = "123"
#     filename = "water.pdb"
#     filepath = "/Users/marat/Downloads/"+filename
#
#     url = F'{STORAGE_ENDPOINT}/{job_id}/{filename}'
#     files = {'file_data': open(filepath, 'rb')}
#
#     r = requests.post(url, files=files)
#
#     print("\n status code ", r.status_code, url)
#     assert r.status_code == 201
#
#     filepath = "/Users/marat/tmp/bigfile1"
#     filename = os.path.basename(filepath)
#     # generate_big_random_bin_file(filepath, 500)
#     gen_big_file(filepath, 500)
#     job_id = 124
#     url = F'{STORAGE_ENDPOINT}/{job_id}/{filename}'
#     files = {'file_data': open(filepath, 'rb')}
#     r = requests.post(url, files=files)
#     assert r.status_code == 201
#
#     r = requests.get(url)
#     print("\n status code ", r.status_code)
#     with open(filepath+"_1", 'wb') as f:
#         f.write(r.content)
#
#     assert filecmp.cmp(filepath+"_1",filepath)
#
#
