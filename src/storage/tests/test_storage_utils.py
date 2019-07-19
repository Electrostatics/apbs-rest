import unittest
from minio import Minio
from minio.error import ResponseError
from os import environ, mkdir, path, rmdir, remove, getcwd, stat
from shutil import rmtree
import hashlib, docker
from service import storage_utils

PORT = '9001'
MINIO_URL=f'localhost:{PORT}'
MINIO_ACCESS_KEY='xxx'
MINIO_SECRET_KEY='yyyyyyyy'
MINIO_JOB_BUCKET='jobs'
STORAGE_CACHE_DIR='.minio_cache'


class StorageUtilsTest(unittest.TestCase):
    def setUp(self):
        # Start MinIO docker container
        # Create test job bucket
        self.minio_name = 'test_storage_utils'
        docker_client = docker.from_env()
        # docker_client.images.pull('minio/minio:latest')
        self.minio_container = docker_client.containers.run(
                                    'minio/minio:RELEASE.2019-07-10T00-34-56Z', 
                                    'server /data',
                                    name=self.minio_name,
                                    ports={'9000/tcp':PORT},
                                    detach=True,
                                    environment={
                                        'MINIO_ACCESS_KEY': MINIO_ACCESS_KEY,
                                        'MINIO_SECRET_KEY': MINIO_SECRET_KEY,
                                    }
                                )

        self.storage_client = storage_utils.StorageClient(  MINIO_URL,
                                                            STORAGE_CACHE_DIR,
                                                            access_key=MINIO_ACCESS_KEY,
                                                            secret_key=MINIO_SECRET_KEY,
                                                            job_bucket_name=MINIO_JOB_BUCKET
                                                        )

        
        self.test_dir = 'test'
        self.test_file = 'test/testfile.txt'
        # self.test_file = path.join('.test', 'test_file.txt')
        if not path.isdir(self.test_dir):
            mkdir(self.test_dir)
        else:
            rmtree(self.test_dir)
            mkdir(self.test_dir)
            # raise Exception('Attempted to create "test" directory; directory exists.')
        with open(self.test_file, 'wb') as fout:
            fout.write(b'hello world\n')

        self.minio_client = storage_utils.get_minio_client(MINIO_URL, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
        # self.minio_client.make_bucket(MINIO_JOB_BUCKET)

    def tearDown(self):
        # del self.minio_client
        # del self.storage_client

        # delete test file
        remove(self.test_file)
        rmdir(self.test_dir)
        rmtree(STORAGE_CACHE_DIR)

        # shutdown and remove container
        self.minio_container.stop()
        self.minio_container.remove()
        pass

    def test_put_object(self):
        '''
            Control
                - put file in bucket
                - retrieve file from bucket with control client
                - compute md5
            Test
                - put file in bucket via StorageClient function
                - retrieve file from bucket with control client
                - compute md5
            Assert
                - compare both md5 hashes
        '''
        obj_name = self.test_file
        with open(self.test_file, 'rb') as fin:
            # Control
            self.minio_client.put_object(MINIO_JOB_BUCKET, obj_name, fin, stat(obj_name).st_size)
            obj_stream  = self.minio_client.get_object(MINIO_JOB_BUCKET, obj_name)
            obj_data    = obj_stream.read()
            control_md5 = hashlib.md5(obj_data).hexdigest()
            fin.seek(0)

            # Clean
            self.minio_client.remove_object(MINIO_JOB_BUCKET, obj_name)

            # Test
            self.storage_client.put_object(MINIO_JOB_BUCKET, obj_name, fin)
            obj_stream  = self.minio_client.get_object(MINIO_JOB_BUCKET, obj_name)
            obj_data    = obj_stream.read()
            test_md5    = hashlib.md5(obj_data).hexdigest()

        # Assert
        self.assertEqual(control_md5, test_md5)

    def test_get_object(self):
        '''
            Control
                - put file in bucket with control client
                - retrieve file from bucket with control client
                - compute md5
            Test
                - put file in bucket with control client
                - retrieve file from bucket via StorageClient function
                - compute md5
            Assert
                - compare both md5 hashes
        ''' 
        obj_name = self.test_file
        with open(self.test_file, 'rb') as fin:
        
        # Control
            # obj_fpath   = path.join(STORAGE_CACHE_DIR, obj_name)
            obj_fpath   = '%s/%s' % (STORAGE_CACHE_DIR, obj_name)
            self.minio_client.put_object(MINIO_JOB_BUCKET, obj_name, fin, stat(obj_name).st_size)
            self.minio_client.fget_object(MINIO_JOB_BUCKET, obj_name, obj_fpath)
            with open(obj_fpath, 'rb') as obj_fin:
                obj_data = obj_fin.read()
            # obj_data    = open(obj_fpath, 'rb').read()
            control_md5 = hashlib.md5(obj_data).hexdigest()
            fin.seek(0)
            
        # Clean
            self.minio_client.remove_object(MINIO_JOB_BUCKET, obj_name)
            remove(obj_fpath)
            # print()
            # print(obj_fpath)
            # print()

        # Test
            self.minio_client.put_object(MINIO_JOB_BUCKET, obj_name, fin, stat(obj_name).st_size)
            obj_fpath   = self.storage_client.fget_object(MINIO_JOB_BUCKET, obj_name)
            with open(obj_fpath, 'rb') as obj_fin:
                obj_data = obj_fin.read()
            # obj_data    = open(obj_fpath, 'rb').read()

            test_md5    = hashlib.md5(obj_data).hexdigest()

        # Assert
        # print(control_md5)
        # print(test_md5)
        self.assertEqual(control_md5, test_md5)

    # @unittest.expectedFailure
    def test_remove_objects(self):
        import random
        '''
            Control
                - put two objects
                - remove random one
                - iterate and compile etag into list
            Assert
                - etag lists are identical
        '''
        control_list = []
        test_list    = []
        num_list = [1, 2, 3, 4, 5]
        # rand_nums = random.choices(num_list, k=2)
        rand_nums = random.sample(num_list, k=2)
        # print('Chosen Random numbers')
        # print(rand_nums)

        obj_name = self.test_file
        obj_list = [f'{obj_name}-{n}' for n in rand_nums]
        # print('Object list')
        # print(obj_list)
        with open(self.test_file, 'rb') as fin:

            # Control
            for num in num_list:
                # print(num)
                # print(f'{obj_name}-{num}')
                self.minio_client.put_object(MINIO_JOB_BUCKET, f'{obj_name}-{num}', fin, stat(obj_name).st_size)
                fin.seek(0)
            
            for del_err in self.minio_client.remove_objects(MINIO_JOB_BUCKET, obj_list):
                print("Deletion Error: {}".format(del_err))
            bucket_objs = self.minio_client.list_objects(MINIO_JOB_BUCKET, prefix=self.test_dir+'/')
            # print('\nBucket Objects')
            for obj in bucket_objs:
                # print(f'   {obj.object_name}')
                control_list.append(obj.object_name)

            # Clean
            self.minio_client.remove_objects(
                MINIO_JOB_BUCKET,
                [f'{obj_name}-{num}' for num in num_list]
            )

            # Test
            for num in num_list:
                self.minio_client.put_object(MINIO_JOB_BUCKET, f'{obj_name}-{num}', fin, stat(obj_name).st_size)
                fin.seek(0)
            self.storage_client.remove_objects(MINIO_JOB_BUCKET, [f'{obj_name}-{n}' for n in rand_nums])
            # self.minio_client.remove_object(MINIO_JOB_BUCKET, f'{obj_name}_{num}')
            for obj in self.minio_client.list_objects(MINIO_JOB_BUCKET, prefix=self.test_dir+'/'):
                test_list.append(obj.object_name)

        # Assert
        # print('\nSorted control/test lists')
        # print(sorted(control_list))
        # print(sorted(test_list))
        self.assertListEqual(control_list, test_list)
        self.assertEqual(len(test_list), 3)
        pass


def main():
    docker_client = docker.from_env()
    docker_client.images.pull('minio/minio:latest')
    unittest.main()

if __name__ == "__main__":
    main()