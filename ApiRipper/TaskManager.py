import sys
import time
import threading
import subprocess
import multiprocessing
import psycopg2
import configparser
from redis import Redis
from rq import Queue as RedisQueue
from ApiRipper import Queue, Common, DBHelper

class TaskManager:
    def __init__(self, db_helper):
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
        self.db_helper = db_helper
        
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
                    task = self.tasks.peek()
                    if status == 'finished':
                        result = task.result
                        if(result is not None):
                            self.db_helper.execute(result)
                    elif status == 'failed':
                        print('Task failed')
                    else:
                        print('Unhandled status: ' + status)
                    self.tasks.pop()
                    self.cull_count += 1
        
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