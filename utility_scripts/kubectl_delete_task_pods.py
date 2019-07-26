import subprocess

if __name__ == "__main__":
    
    # Get kubectl pods
    command = 'kubectl get pods'
    p1 = subprocess.Popen(command.split(), stdout=subprocess.PIPE)

    # Parse kubectl pods which begin with "task-"
    command = 'grep ^task-'
    p2 = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stdin=p1.stdout)

    output, err = p2.communicate()
    # print(output)

    # Remove dead pods from cluster
    if output:
        for line in output.split('\n'):
            spl_line = line.split()
            if len(spl_line) > 0:
                task_name = spl_line[0]
                command = 'kubectl delete pods %s' % spl_line[0]
                p3 = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                output, err = p3.communicate()
                print(output.strip())