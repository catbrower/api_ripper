import time
import threading
import multiprocessing
import psycopg2
import configparser
from redis import Redis
from rq import Queue as RedisQueue
from ApiRipper import Queue
from ApiRipper import Common

class TaskManager:
    def do_sql(sql_string):
        print(sql_string)
        
    def cull_tasks(tasks, cull_count):
        while(True):
            len = tasks.length()
            if tasks.peek() is not None:
                status = tasks.peek().get_status()
                while tasks.peek().get_status() == 'finished':
                    do_sql(tasks.pop().result)
                    cull_count += 1

                #check for status 'failed'
            # time.sleep(0.1)

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.conf')

        # self.num_threads = 2 * int(multiprocessing.cpu_count()) - 1
        self.num_threads = 24
        self.queue_index = 0
        self.queues = []
        self.tasks = Queue.Queue()
        self.cull_count = 0
        self.cull_tasks_thread = threading.Thread(target=TaskManager.cull_tasks, args=[self.tasks, self.cull_count])
        self.cull_tasks_thread.start()

        for i in range(self.num_threads):
            # conn = psycopg2.connect('dbname=' + config['sql']['dbname'] + ' user=' + config['sql']['user'])
            # cur = conn.cursor()
            self.queues.append(RedisQueue(connection=Redis()))

    def do_task(self, task, args):
        qi = self.queue_index
        new_task = self.queues[qi].enqueue(task, args, result_ttl=60)
        self.tasks.push(new_task)
        self.queue_index = qi + 1 if qi < len(self.queues) - 1 else 0

    def num_completed_tasks(self):
        return self.cull_count

    def reset(self):
        self.queue_index = 0
        self.cull_count = 0
        self.tasks = []
        #might have to clear the queue too I dunno

    def allTasksComplete(self):
        return len(self.tasks) == 0