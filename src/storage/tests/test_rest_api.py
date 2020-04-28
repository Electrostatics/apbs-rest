#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This is the module."""

# !/usr/bin/python
# -*- coding: utf-8 -*-
from pathlib import Path

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
def services():
    """
    setup/teardown for storage rest servicec
    """
    print("creating services")

    try:
        subprocess.check_call(["docker-compose", "build"])
        subprocess.check_call(["docker-compose", "up", "-d"])
        sleep(2)
        yield
    finally:
        print("\n stopping services")
        subprocess.check_call(["docker-compose", "down"])


@pytest.fixture(scope="module")
def test_data(tmpdir_factory):
    """
    create data files
    """
    print("creating data files")

    sizes = (100, 200, 300)

    files = []
    for size in sizes:
        filename = F"file{size}"
        filepath = tmpdir_factory.mktemp("data") / filename
        gen_big_file(filepath, size)
        files.append(Path(filepath))

    assert True
    return files


def test_flask_server(services, test_data):
    r = requests.request("GET", FLASK_HOST)

    assert r.status_code == 200


def test_upload(services, test_data, tmp_path):

    test_files = test_data

    job_id = 12345

    for filepath in test_files:
        filename = filepath.name
        url = F'{STORAGE_ENDPOINT}/{job_id}/{filename}'
        files = {'file_data': filepath.open('rb')}
        r = requests.post(url, files=files)
        assert r.status_code == 201

    for filepath in test_files:
        filename = filepath.name
        url = F'{STORAGE_ENDPOINT}/{job_id}/{filename}'
        r = requests.get(url)
        download_path = tmp_path / filename
        assert r.status_code == 200
        with download_path.open('wb') as f:
            f.write(r.content)

        assert filecmp.cmp(download_path, filepath)
    #

    # filepath = tmp_path / "bigfile1"
    # filename = filepath.name
    #
    # gen_big_file(filepath, 100)
    # job_id = 124
    # url = F'{STORAGE_ENDPOINT}/{job_id}/{filename}'
    # files = {'file_data': filepath.open('rb')}
    # r = requests.post(url, files=files)
    # assert r.status_code == 201

#
# def test_upload(services, tmp_path):
#
#     filepath = tmp_path / "bigfile1"
#     filename = filepath.name
#
#     gen_big_file(filepath, 100)
#     job_id = 124
#     url = F'{STORAGE_ENDPOINT}/{job_id}/{filename}'
#     files = {'file_data': filepath.open('rb')}
#     r = requests.post(url, files=files)
#     assert r.status_code == 201
#
#     r = requests.get(url)
#     filepath1 = tmp_path / "bigfile2"
#     print("\n status code ", r.status_code)
#     with filepath1.open('wb') as f:
#         f.write(r.content)
#
#     assert filecmp.cmp(filepath1,filepath)
#
#
