import requests, json, mysql.connector
# from os import getenv
# from sys import stderr
# from time import sleep
# from queue import Queue
# from threading import Thread
# from dotenv import load_dotenv

def update_workflow_to_running(cnx:mysql.connector.MySQLConnection, job_id):
    query = f"UPDATE workflows SET workflow_status='running' WHERE job_id='{job_id}'"
    cursor = cnx.cursor()
    cursor.execute(query)
    cursor.close()
    cnx.commit()

def update_task_to_running(cnx:mysql.connector.MySQLConnection, job_id, workflow_new_status=None):
    if workflow_new_status is None:
        query = f"UPDATE workflows SET task_status='running' WHERE job_id='{job_id}'"
    else:
        query = f"UPDATE workflows SET task_status='running', workflow_status='{workflow_new_status}' WHERE job_id='{job_id}'"

    cursor = cnx.cursor()
    cursor.execute(query)
    cursor.close()
    cnx.commit()

def update_task_to_terminated(cnx:mysql.connector.MySQLConnection, job_id, job_state, task_files):
    task_files_query = f"SELECT task_output FROM workflows WHERE job_id='{job_id}'"
    cursor = cnx.cursor()
    cursor.execute(task_files_query)
    for row in cursor:
        current_files = json.loads(row[0])
        current_files.append(task_files)
    cursor.close()
    current_files = json.dumps(current_files)
        
    updated_query = f"UPDATE workflows SET task_status='{job_state}', task_output='{current_files}' WHERE job_id='{job_id}'"
    cursor = cnx.cursor()
    cursor.execute(updated_query)
    cursor.close()
    cnx.commit()

def get_pending_tasks(cnx:mysql.connector.MySQLConnection):
    query = f"SELECT * FROM workflows WHERE task_status='pending';"
    cursor = cnx.cursor()
    cursor.execute(query)

    all_pending = []
    for row in cursor:
        all_pending.append(row)

    cursor.close()
    return all_pending

def get_running_tasks(cnx:mysql.connector.MySQLConnection):
    query = f"SELECT * FROM workflows WHERE task_status='running';"
    cursor = cnx.cursor()
    cursor.execute(query)

    all_running = []
    for row in cursor:
        all_running.append(row)

    cursor.close()
    return all_running

def get_completed_tasks(cnx:mysql.connector.MySQLConnection):
    # Returns completed tasks for only for in-progress workflows
    query = f"SELECT * FROM workflows WHERE workflow_status='running' and task_status='complete';"
    cursor = cnx.cursor()
    cursor.execute(query)

    all_running = []
    for row in cursor:
        all_running.append(row)

    cursor.close()
    return all_running