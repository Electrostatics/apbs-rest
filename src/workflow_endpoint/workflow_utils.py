# import requests
import mysql.connector
from os import getenv
try:
    from simplejson import loads
except:
    from json import loads

class WorkflowInfo():
    def __init__(self, job_id, mysql_cnx):
        self.job_id = job_id
        self.cnx = mysql_cnx
        self.workflow_info = self.get_workflow_info(self.job_id, self.cnx)
        self.refresh()

    def refresh(self):
        self.workflow_info = self.get_workflow_info(self.job_id, self.cnx)
        if self.workflow_info is not None:
            job_id, workflow_str, workflow_status, current_task, current_task_status, all_task_params, all_task_output = self.workflow_info
            all_task_params = loads(all_task_params)
            all_task_output = loads(all_task_output)

            self.workflow_str = workflow_str
            self.workflow_status = workflow_status
            self.current_task_index = current_task
            self.current_task_status = current_task_status
            self.all_task_params = all_task_params
            self.all_task_output = all_task_output

            self.num_tasks = len(self.workflow_str.split(';'))

    def get_workflow_info(self, job_id, mysql_cnx):
        workflow_info = None
        table_name = getenv('DATABASE_TABLE')
        query = f"SELECT * FROM {table_name} WHERE job_id='{job_id}'"
        
        cursor = mysql_cnx.cursor()
        cursor.execute(query)

        for row in cursor:
            workflow_info = row
        cursor.close()
        # print(type(workflow_info))
        print(workflow_info)
        return workflow_info

    def get_starttime(self, task_index=None):
        if task_index is None:
            task_index = self.current_task_index
        elif task_index > self.num_tasks-1:
            task_index = self.num_tasks-1
        task_output = self.all_task_output[task_index]
        print('================================')
        print(task_index)
        print(task_output)
        print('================================\n')

        start_time = task_output['startTime']
        return start_time


    def get_endtime(self, task_index=None):
        if task_index is None:
            task_index = self.current_task_index
        elif task_index > self.num_tasks-1:
            task_index = self.num_tasks-1
        task_output = self.all_task_output[task_index]

        end_time = task_output['endTime']
        return end_time


    def get_task_state(self, task_index=None):
        if task_index is None:
            task_index = self.current_task_index
        elif task_index > self.num_tasks-1:
            task_index = self.num_tasks-1
        task_output = self.all_task_output[task_index]

        task_state = task_output['status']
        return task_state

    def get_task_output_files(self, task_index=None):
        if task_index is None:
            task_index = self.current_task_index
        elif task_index > self.num_tasks-1:
            task_index = self.num_tasks-1
        task_output = self.all_task_output[task_index]

        task_files = task_output['files']
        return task_files

    def extract_workflow_state(self):
        return self.workflow_status