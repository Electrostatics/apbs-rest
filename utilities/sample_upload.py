import requests, sys
from pprint import pprint

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = '../tests/sample_input/1a1p.pqr'
    files = {'file_data': open(file_name, 'rb')}

    url = 'http://apbs.192.168.99.100.xip.io/storage'
    job_id = 'sample_job_id'

    print(f'Uploading {file_name}')

    obj_name = file_name.split('/')[-1]

    # r = requests.post(f'{url}/{job_id}/1a1p.pqr', files=files)
    r = requests.post(f'{url}/{job_id}/{obj_name}', files=files)
    print(r.status_code)
    pprint(r.content)


    # r = requests.get(f'{url}/{job_id}/1a1p.pqr?json=true')
    r = requests.get(f'{url}/{job_id}/{obj_name}?json=true')
    print(r.status_code)
    # pprint(r.content.decode('utf-8').replace('\\n', '\n'))
