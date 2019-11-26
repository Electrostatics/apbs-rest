import subprocess, time, sys
from io import StringIO

def get_deploy():
    kubectl_output = subprocess.check_output(['kubectl', 'get', 'deploy'])
    kubectl_output = kubectl_output.decode('utf-8')
    
    return kubectl_output

def get_undeployed(deployment_output):
    header_line = ''
    undeployed_services = []
    for deployment in StringIO(deployment_output):
        fields = deployment.split()
        if fields == ['NAME', 'READY', 'UP-TO-DATE', 'AVAILABLE', 'AGE']:
            header_line = deployment.strip()
        elif fields[0].startswith('apbs-rest-'):
            if fields[1] == '0/1':
                undeployed_services.append(deployment.strip())
        else:
            pass

    return undeployed_services, header_line

if __name__ == "__main__":
    # Check arguments
    try:
        retry_timer = int(sys.argv[1])
        max_retries = int(sys.argv[2])
    except:
        print("USAGE: python wait_for_deployments.py NUM_WAIT_SECONDS NUM_RETRIES", file=sys.stderr)
        if len(sys.argv) > 2:
            print("Arguments must be integers." % sys.argv[1], file=sys.stderr)
        else:
            print("Not enough arguments. Please provide two integer argument.", file=sys.stderr)
        sys.exit(1)


    deployment_output = get_deploy()
    undeployed, header = get_undeployed(deployment_output)
    
    num_attempt = 1
    while len(undeployed) > 0 and num_attempt <= max_retries:
        # Print undeployed services to stdout
        print('Attempt #%d' % num_attempt)
        print('  %s' % header)
        for service in undeployed:
            print('  %s' % service)

        # sleep n seconds then try again
        print('\nRetry in %d seconds' % (retry_timer))
        time.sleep(retry_timer)
        deployment_output = get_deploy()
        undeployed, header = get_undeployed(deployment_output)
        num_attempt += 1

    if num_attempt < max_retries:
        print('All deployments for APBS-REST are up!!! Exiting.')
    else:
        print('Deployments not launched in max number of retries: %d' % max_retries, file=sys.stderr)
        sys.exit(1)