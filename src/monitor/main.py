import requests, json, mysql.connector
from monitor_utils import *
from os import getenv
from sys import stderr
from time import sleep
from queue import Queue
from threading import Thread
from dotenv import load_dotenv
load_dotenv()

from pprint import pprint

# TASK_HOST = getenv('TASK_HOST', default='http://localhost:5004')
TASK_HOST = getenv('TASK_HOST', default='')

HOST      = getenv('DATABASE_HOST')
PORT      = getenv('DATABASE_PORT')
DBNAME    = getenv('DATABASE_NAME')
USER      = getenv('DATABASE_USER')
PASSWORD  = getenv('DATABASE_PASSWORD')

def monitor_database_for_pending_tasks(pending_queue):
    print('monitoring from database')

    cnx = mysql.connector.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DBNAME
    )

    # while True:
        # sleep(3)
    if True:
        print('  checking database for tasks...')
        # query database for unfulfilled tasks, download tasks and parameters
        # for each task:
            # enqueue the task
            # update database that task is in queue
        pending_task_list = get_pending_tasks(cnx)
        for task in pending_task_list:

            job_id, workflow, workflow_status, current_task_index, task_status, all_params, task_files = task
            
            print('    parsing job id:          ' + job_id)

            tasks_within_workflow = workflow.split(';')
            # params_within_workflow = all_params.split(';')
            params_within_workflow = json.loads(all_params)

            print('    pending_task_list size: %d' % len(pending_task_list))
            print('    params_within_workflow size: %d' % len(params_within_workflow))
            print('    tasks_within_workflow size: %d' % len(tasks_within_workflow))

            current_task   = tasks_within_workflow[current_task_index]
            current_params = params_within_workflow[current_task_index]
            print('    current_task: %s' % (current_task))
            print('    current_task_index: %s' % (current_task_index))

            task = {
                'job_id': job_id,
                'task_name': current_task,
                'task_params': current_params
            }
            # pprint(task)
            pending_queue.put((task, workflow_status))
    cnx.close()

def send_pending_tasks_from_queue(pending_queue, running_list):
    cnx = mysql.connector.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DBNAME
    )

    print('monitoring from queue')
    # while True:
    if True:
        if pending_queue.empty():
            print('  queue is empty. sleeping...')
            # sleep(1)
        else:
            # send task to task service

            while not pending_queue.empty():
                print(pending_queue.qsize())
                item, workflow_status = pending_queue.get()
                print(pending_queue.qsize())
                job_id  = item['job_id']
                task_name   = item['task_name']
                task_params = item['task_params']
                response = requests.post('%s/api/task/%s/%s' % (TASK_HOST, job_id, task_name), json=task_params)
                # print('    %s/api/task/%s/%s\n%s' % (TASK_HOST, job_id, task_name, task_params))
                if response.status_code == 202:
                    # update task to 'running' after sending; update the workflow's status to 'running' if this the first
                    if workflow_status == 'pending':
                        print('updating workflow to running')
                        update_task_to_running(cnx, job_id, workflow_new_status='running')
                    else:
                        update_task_to_running(cnx, job_id)
                    running_list.append((job_id, task_name))
                    # continue
                else:
                    print('error: sending the task %s:%s returned status code %d' % (str(job_id), task_name, response.status_code), file=stderr)
    
    cnx.close()

def inquire_status_for_completed_tasks(running_list, complete_queue):
    cnx = mysql.connector.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DBNAME
    )

    # while True:
        # sleep(1)
    if True:
        completed_indices = []

        # for every task that's running,
        #   get the status, place in completion queue
        for i in range(len(running_list)):
            job_id, task_name = running_list[i]
            status_response = requests.get('%s/api/task/%s/%s' % (TASK_HOST, job_id, task_name))
            if status_response.status_code == 200:
                # from pprint import pprint
                # pprint(json.loads(status_response.content))
                task_info = json.loads(status_response.content)[task_name]
                # pprint(task_info)
                task_status = task_info['status']
                task_files = task_info['files']
                if task_status != 'running':
                    # complete_queue.put((job_id, task_status, task_files))
                    complete_queue.put((job_id, task_status, task_info))
                    completed_indices.append(i)
        
        # Traverses in revers order so as not to shift the index order
        #   of running_list as we pop each respective element
        for index in completed_indices[::-1]:
            running_list.pop(index)

        while not complete_queue.empty():
            # Update database that task is in a terminated state (i.e. 'complete' or 'error')
            job_id, task_status, task_files = complete_queue.get()
            update_task_to_terminated(cnx, job_id, task_status, task_files)

    cnx.close()

def update_database_to_next_tasks():
    # For any completed tasks with workflow_status == 'running',
    #   increment current_task number if not the last (len(workflow) - 1)

    cnx = mysql.connector.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        database=DBNAME
    )
    # while True:
    if True:
        # query = f"SELECT * FROM workflows WHERE workflow_status='running' and task_status='complete';"
        # cursor = cnx.cursor()
        # cursor.execute(query)
        # for task in cursor:
        completed_task_list = get_completed_tasks(cnx)
        for task in completed_task_list:
            job_id, workflow, workflow_status, current_task_index, task_status, all_params, all_task_files = task

            new_task_index = None
            if current_task_index == ( len(workflow.split(';'))-1 ):
                query = f"UPDATE workflows SET workflow_status='complete' WHERE job_id='{job_id}'"
                cursor = cnx.cursor()
                cursor.execute(query)
            else:
                new_task_status = 'pending'
                new_task_index = current_task_index + 1
                query = f"UPDATE workflows SET current_task='{new_task_index}', task_status='{new_task_status}' WHERE job_id='{job_id}'"
                cursor = cnx.cursor()
                cursor.execute(query)

        # cursor.close()
        cnx.commit()

    cnx.close()

def main():
    pending_queue = Queue(maxsize=0) # infinite queue size for now
    # running_list = Queue(maxsize=0)
    running_list = []
    complete_queue = Queue(maxsize=0)

    # t1 = Thread(target=monitor_database_for_pending_tasks, args=(pending_queue,))
    # t2 = Thread(target=send_pending_tasks_from_queue, args=(pending_queue, running_list))
    # t3 = Thread(target=inquire_status_for_completed_tasks, args=(running_list, complete_queue))
    # t4 = Thread(target=update_database_to_next_tasks)

    # # t1.daemon = False
    # # t2.daemon = False

    # t1.start()
    # t2.start()
    # t3.start()
    # t4.start()

    # t1.join()
    # t2.join()
    # t3.join()
    # t4.join()

    while True:
        sleep(1)
        monitor_database_for_pending_tasks(pending_queue)
        send_pending_tasks_from_queue(pending_queue, running_list)
        inquire_status_for_completed_tasks(running_list, complete_queue)
        update_database_to_next_tasks()
        print()

if __name__ == "__main__":
    main()