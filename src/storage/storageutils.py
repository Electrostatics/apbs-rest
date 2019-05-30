from __future__ import print_function
from minio import Minio
from minio.error import ResponseError
from shutil import rmtree
import os, hashlib, sys

class StorageClient:
    def __init__(self, storage_url, cache_dir_path, access_key=None, secret_key=None):
        self.cache_path = os.path.abspath(cache_dir_path)

        if access_key and secret_key:
            self.__minio_client = get_minio_client(storage_url, access_key, secret_key)

        '''Utilize tempfile module in future'''
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

    def get_object(self, bucket_name, object_name, request_headers=None):
        data = None
        if not self.inside_cache(bucket_name, object_name):
            '''Retrieve object from bucket, saving to local file system'''
            data = self.__minio_client.get_object(bucket_name, object_name, request_headers=request_headers)
            data = data.read()
            # data = 'object retrieved from bucket'
            print('object retrieved from bucket')
            # object_path = save_path

        else:
            '''Retrieve file path from file system'''
            object_path = os.path.join(self.cache_path, object_name)
            with open(object_path, 'r') as fin:
                data = fin.read()

            # data = 'object retrieved from cache'
            print('object retrieved from cache')

        return data

    def fget_object(self, bucket_name, object_name, request_headers=None):
        """ 
            Checks if object_name exists in local storage,
            otherwise the object is retreived from bucket/blob
        """
        data = None
        object_path = None
        if not self.inside_cache(bucket_name, object_name):
            '''Retrieve object from bucket, saving to local file system'''
            save_path = os.path.join(self.cache_path, object_name)
            self.__minio_client.fget_object(bucket_name, object_name, save_path, request_headers=request_headers)

            # data = 'object retrieved from bucket'
            print('object retrieved from bucket')
            object_path = save_path

        else:
            '''Retrieve file path from file system'''
            object_path = os.path.join(self.cache_path, object_name)
            # with open(object_path, 'r') as fin:
            #     data = fin.read()

            # data = 'object retrieved from cache'
            print('object retrieved from cache')

        # return data
        return object_path

    def put_object(self, bucket_name, object_name, data, length=None,
                   content_type='application/octet-stream', metadata=None):
        '''Before sending to bucket, save locally'''

        '''CONSIDER CHANGING data TO MORE SELF-EXPLANATORY NAME, LIKE fin'''
        file_path = os.path.join(self.cache_path, object_name)
        self.save_to_local(file_path, data.read())
        data.seek(0)

        if length is None:
            length = os.stat(file_path).st_size

        try:
            etag_str = self.__minio_client.put_object(bucket_name, object_name, data, 
                                                    length, 
                                                    # os.stat(file_path).st_size, 
                                                    content_type=content_type, 
                                                    metadata=metadata)
            return etag_str
        except ResponseError as err:
            sys.stderr.write(err)

    def remove_objects(self, bucket_name, objects_iter):
        try:
            # delete object files from local cache
            for object_name in objects_iter:
                file_path = os.path.join(self.cache_path, object_name)
                self.remove_from_local(file_path)

            for del_err in self.__minio_client.remove_objects(bucket_name, objects_iter):
                print("Deletion Error: {}".format(del_err), file=sys.stderr)
        except ResponseError as err:
            print(err, file=sys.stderr)
        pass

    def list_objects(self, bucket_name, prefix=None, recursive=False):
        object_list = self.__minio_client.list_objects(bucket_name,
                                                     prefix=prefix,
                                                     recursive=recursive)
        return object_list

    def get_local_etag(self, file_name):
        '''Compute etag of local file used by S3'''
        data = None
        with open(file_name, 'rb') as fin:
            data = fin.read()
        etag = hashlib.md5(data)
        etag = str(etag.hexdigest())

        return etag

    def save_to_local(self, file_path, data):
        dir_name = os.path.dirname(file_path)

        # create job dir if it doesn't exist
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        # open file from path, overwrite data, close
        with open(file_path, 'wb') as fout:
            fout.write(data)

    def remove_from_local(self, file_path):
        dir_name = os.path.dirname(file_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        if os.path.exists(dir_name):
            # removes job directory if empty
            if len(os.listdir(dir_name)) == 0:
                os.rmdir(dir_name)

    def clear_cache(self):
        """Deletes ALL contents of the cache directory"""
        for f in os.listdir(self.cache_path):
            file_path = os.path.join(self.cache_path, f)
            if os.path.isdir(file_path):
                rmtree(file_path)
            else:
                os.remove(file_path)

    # def inside_cache(self, dir_name, file_name):
    def inside_cache(self, bucket_name, object_name):
        """ Compares etags of bucket with MD5 hash of local
            Returns true if they match, false otherwise
        """
        dir_name, file_name = object_name.split('/')
        path = os.path.join(self.cache_path, dir_name, file_name)

        if os.path.exists(path):
            '''Check if local version is up to date with bucket'''
            bucket_etag = self.__minio_client.stat_object(bucket_name, object_name).etag
            local_etag = self.get_local_etag(path)
            # print('bucket etag: '+ bucket_etag)
            # print('local etag:  '+ local_etag)
            return bucket_etag == local_etag
        else:
            return False
    

def get_minio_client(minio_url, access_key, secret_key):
    minioClient= Minio( minio_url,
                        access_key=access_key,
                        secret_key=secret_key,
                        secure=False)
    return minioClient