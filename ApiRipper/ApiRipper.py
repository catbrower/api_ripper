import sys
import time
import datetime
from datetime import date
import subprocess
from alive_progress import alive_bar
import configparser

from ApiRipper import Common, TaskManager
from ApiRipper.DBHelper import DBHelper

config = configparser.ConfigParser()
config.read('application_properties.conf')
schema = {}
schema_file = open('polygon/schema.py').read()
exec(schema_file, {}, schema)
num_workers = int(config['general']['num_workers'])
db_helper = DBHelper(schema['db_connection_str'])
tm = TaskManager.TaskManager(db_helper)

#Test vars
multithreaded = int(config['testing']['multithreaded']) == 1
task_limit = int(config['testing']['task_limit'])
ignore = [x.strip() for x in config['testing']['ignore'].split(',') if not x.strip() == '']
do_only = [x.strip() for x in config['testing']['do_only'].split(',') if not x.strip() == '']

#Processes
workers = []
# redis_process = None
error_file = open('worker_error.log', 'w')
output_file = open('worker_output.log', 'w')

def run_processes():
    # redis_process = subprocess.Popen(['redis-server'], stdout=output_file, stderr=error_file)
    # time.sleep(1)
    for i in range(0, num_workers):
        workers.append(subprocess.Popen(['rq', 'worker'], stdout=output_file, stderr=error_file))

def exit():
    tm.exit()
    for worker in workers:
        worker.kill()
    # redis_process.kill()
    error_file.close()
    output_file.close()

#Main stuff
if multithreaded:
    run_processes()

for table_key in schema['sql_tables'].keys():
    sql = DBHelper.buildTable(
        table_key, schema['sql_tables'][table_key], schema['sql_table_constraints'][table_key])
    db_helper.execute(sql)

for table_key in schema['endpoints'].keys():
    print('Get ' + table_key)
    if len(ignore) > 0 and table_key in ignore:
        print('Skip')
        continue

    if len(do_only) > 0 and table_key not in do_only:
        print('Skip')
        continue

    ripper = schema['endpoint_rippers']['default']
    if table_key in schema['endpoint_rippers'].keys():
        ripper = schema['endpoint_rippers'][table_key]
    
    urls = []
    for url in ripper(schema, table_key):
        if task_limit >= 0 and len(urls) >= task_limit:
            break
        urls.append(url)

    with alive_bar(len(urls)) as bar:
        for url in urls:
            if multithreaded:
                tm.do_task(Common.get_response, [schema_file, table_key, url])
            else:
                r = Common.get_response([schema_file, table_key, url])
                if r is not None:
                    db_helper.execute(r)
                bar()
                
        tasks_complete = 0
        while not tm.all_tasks_complete():
            time.sleep(0.1)

            for i in range(0, tm.num_completed_tasks() - tasks_complete):
                bar()
            tasks_complete = tm.num_completed_tasks()
    tm.reset()

exit()