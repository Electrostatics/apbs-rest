from minio import Minio
from minio.error import ResponseError
from shutil import rmtree
import os

class StorageCache:
    def __init__(self, dir_path, access_key=None, secret_key=None):
        self.cache_path = os.path.abspath(dir_path)

        if access_key and secret_key:
            self.minio_client = get_minio_client(access_key, secret_key)

        '''Utilize tempfile module in future'''
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

    def fget_object(self, bucket_name, object_name, request_headers=None):
        """ 
            Checks if object_name exists in local storage,
            otherwise the object is retreived from bucket/blob
        """
        data = None
        object_path = None
        if not self.inside_cache(*object_name.split('/')):
            # obj = self.minio_client.get_object(bucket_name, object_name)
            # data = obj.data.decode('utf-8')

            save_path = os.path.join(self.cache_path, object_name)
            self.minio_client.fget_object(bucket_name, object_name, save_path, request_headers=request_headers)
            # self.save_to_local(save_path, data)

            # data = 'object retrieved from bucket'
            print('object retrieved from bucket')
            object_path = save_path

        else:
            '''Retrieve file from file system'''
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
        file_path = os.path.join(self.cache_path, object_name)
        self.save_to_local(file_path, data)

        etag_str = self.minio_client.put_object(bucket_name, object_name, data, 
                                                os.stat(file_path).st_size, 
                                                content_type=content_type, 
                                                metadata=metadata)
        return etag_str

    def save_to_local(self, path, data):
        dir_name = os.path.dirname(path)

        # create job dir if it doesn't exist
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        # open file from path, overwrite data, close
        with open(path, 'w+') as fout:
            fout.write(data)

    def clear_cache(self):
        """Deletes ALL contents of the cache directory"""
        for f in os.listdir(self.cache_path):
            file_path = os.path.join(self.cache_path, f)
            if os.path.isdir(file_path):
                rmtree(file_path)
            else:
                os.remove(file_path)

    def inside_cache(self, dir_name, file_name):
        """"""
        path = os.path.join(self.cache_path, dir_name, file_name)
        print(path)
        return os.path.exists(path)

    

def get_minio_client(access_key, secret_key):
    minioClient = Minio('localhost:9000',
                        access_key=access_key,
                        secret_key=secret_key,
                        secure=False)
    return minioClient