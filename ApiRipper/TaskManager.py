import sys
import time
import threading
import subprocess
import multiprocessing
import psycopg2
import configparser
from redis import Redis
from rq import Queue as RedisQueue
from ApiRipper import Queue
from ApiRipper import Common

class TaskManager:
    def do_sql(self, sql_string):
        pass
        # print(sql_string)
        
    def cull_tasks(self):
        while(True):
            if self.kill_threads:
                break
                
            length = self.tasks.length()
            if self.tasks.peek() is not None:
                status = self.tasks.peek().get_status()
                if status == 'queued' or status == 'started':
                    time.sleep(0.1)
                else:
                    self.cull_count += 1
                    task = self.tasks.pop()
                    if status == 'finished':
                        self.do_sql(task.result)
                    elif status == 'failed':
                        print('Task failed')
                    else:
                        print('Unhandled status: ' + status)

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.conf')

        # self.num_threads = 2 * int(multiprocessing.cpu_count()) - 1
        self.kill_threads = False
        self.num_threads = 100
        # self.queue_index = 0
        self.task_queue = RedisQueue(connection=Redis())
        self.tasks = Queue.Queue()
        self.cull_count = 0
        self.cull_tasks_thread = threading.Thread(target=self.cull_tasks, args=[])
        self.cull_tasks_thread.start()
        self.workers = []
        self.error_file = open('worker_error.log', 'w')
        self.output_file = open('worker_output.log', 'w')
        for i in range(0, self.num_threads):
            self.workers.append(subprocess.Popen(['rq', 'worker'], stdout=self.output_file, stderr=self.error_file))

    def do_task(self, task, args):
        # qi = self.queue_index
        new_task = self.task_queue.enqueue(task, args, result_ttl=60)
        self.tasks.push(new_task)
        # self.queue_index = qi + 1 if qi < len(self.queues) - 1 else 0

    def reset(self):
        self.queue_index = 0
        self.cull_count = 0
        self.tasks = Queue.Queue()
        #might have to clear the queue too I dunno

    def all_tasks_complete(self):
        return self.tasks.length() == 0

    def num_completed_tasks(self):
        return self.cull_count

    def remaining_tasks(self):
        return self.tasks.length()

    def exit(self):
        self.kill_threads = True
        for worker in self.workers:
            worker.kill()
        self.error_file.close()
        self.output_file.close()