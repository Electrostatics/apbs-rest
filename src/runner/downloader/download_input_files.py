from sys import argv
from os import getenv, path
from requests import get

try:
    import simplejson as json
except:
    import json

STORAGE_HOST = getenv('STORAGE_HOST', None)
APP_RUN_DIR  = getenv('APP_RUN_DIR', None)
JOB_ID       = getenv('JOB_ID', None)

class EnvironmentValueError(ValueError):
    def __init__(self, expression):
        self.expression = 'Missing environment variable %s' % expression

if __name__ == "__main__":

    if JOB_ID is None: raise EnvironmentValueError('JOB_ID')
    if APP_RUN_DIR is None: raise EnvironmentValueError('APP_RUN_DIR')
    if STORAGE_HOST is None: raise EnvironmentValueError('STORAGE_HOST')

    print('Downloading...')
    for file_name in argv[1:]:
        print('   %s' % file_name)

        # Get file data from server as JSON
        object_name = '%s/%s' % (JOB_ID, file_name)
        url = '%s/%s/%s?json=true' % (STORAGE_HOST, JOB_ID, file_name)
        response = get(url)
        if response.status_code == 404:
            raise ConnectionError('File %s not found for the JOB_ID %s. Returned HTTP code %d' % (file_name, JOB_ID, response.status_code))
        elif response.status_code >= 500:
            message = 'Server-side error. Returned HTTP code %d.\n    URL: %s' % (response.status_code, url)
            raise ConnectionError(message)
            # raise ConnectionError('Server-side error. Returned HTTP code %d' % (response.status_code))

        # Convert resonse data to string (MAY WANT TO ADJUST FOR BINARY DATA)
        object_str = json.loads(response.content)[object_name]

        #save text to file
        with open(path.join(APP_RUN_DIR, file_name), 'w') as fout:
            fout.write(object_str)

    print('...done')