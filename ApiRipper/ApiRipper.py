import sys
import time
import datetime
from datetime import date
import subprocess
from alive_progress import alive_bar

from ApiRipper import Common
from ApiRipper import TaskManager

schema = {}
schema_file = open('polygon/schema.py').read()
exec(schema_file, {}, schema)
ignore = ['aggregates', 'minute', 'ticker_detail', 'trades', 'market_status', 'holidays']
do_only = ['tickers']
multithreaded = True
task_limit = 100
num_workers = 100
tm = TaskManager.TaskManager()

#Processes
workers = []
redis_process = None
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

for table_key in schema['endpoints'].keys():
    if len(ignore) > 0 and table_key in ignore:
        continue

    if len(do_only) > 0 and table_key not in do_only:
        continue

    ripper = schema['endpoint_rippers']['default']
    if table_key in schema['endpoint_rippers'].keys():
        ripper = schema['endpoint_rippers'][table_key]
    
    urls = []
    print('Get ' + table_key)
    for url in ripper(schema, table_key):
        if task_limit >= 0 and len(urls) >= task_limit:
            break
        urls.append(url)

    with alive_bar(len(urls)) as bar:
        for url in urls:
            if multithreaded:
                tm.do_task(Common.get_response, [schema_file, table_key, url])
            else:
                Common.get_response(schema_file, table_key, url)

        #iterate over num_complete_tasks to print bar

        tasks_complete = 0
        while not tm.all_tasks_complete():
            time.sleep(1)

            for i in range(0, tm.num_completed_tasks() - tasks_complete):
                bar()
            tasks_complete = tm.num_completed_tasks()
            # print(tm.remaining_tasks())
    # with alive_bar(num_pages) as bar:
    #     bar()

    tm.reset()

exit()