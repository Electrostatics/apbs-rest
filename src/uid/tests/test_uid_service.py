import unittest
from main import app

try:
    import simplejson as json
except ImportError:
    import json

class UIDServiceTest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_liveness_path(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), '')

        response = self.client.get('/check/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), '')

    def test_get_uid_generator(self):
        response = self.client.get('/api/uid/')
        data_json = json.loads(response.data)
        
        self.assertEqual(response.content_type, 'application/json')
        self.assertIn('job_id', data_json.keys())
        self.assertIsInstance(data_json['job_id'], str)

        
    def test_uid_uniqueness(self):
        uid_list = []
        for i in range(5000):
            response = self.client.get('/api/uid/')
            data_json = json.loads(response.data)
            uid_list.append(data_json['job_id'])

        # Checks that all the IDs generated are unique
        self.assertEqual(len(uid_list), len(set(uid_list)), msg='IDs generated not always unique')

if __name__ == "__main__":
    unittest.main()