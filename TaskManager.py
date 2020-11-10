import time
import threading
import multiprocessing
import psycopg2
import configparser
from redis import Redis
from rq import Queue as RedisQueue
from Queue import Queue

class TaskManager:
    RQ_INDEX = 0
    PSQL_INDEX = 1

    def cull_tasks(tasks):
        while(True):
            while tasks.peek() is not None and tasks.peek().get_status() == 'finished':
                tasks.pop()
            time.sleep(0.1)

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.conf')

        # self.num_threads = 2 * int(multiprocessing.cpu_count()) - 1
        self.num_threads = 24
        self.queue_index = 0
        self.queues = []
        self.tasks = Queue()
        self.cull_tasks_thhread = threading.Thread(target=TaskManager.cull_tasks, args=(self.tasks))

        for i in range(self.num_threads):
            conn = psycopg2.connect('dbname=' + config['sql']['dbname'] + ' user=' + config['sql']['user'])
            cur = conn.cursor()
            self.queues.append([RedisQueue(connection=Redis()), conn, cur])

    def doTask(self, task, args):
        qi = self.queue_index
        new_task = self.queues[qi][TaskManager.RQ_INDEX].enqueue(task, self.queues[qi][TaskManager.PSQL_INDEX] + args)
        self.tasks.push(new_task)
        self.queue_index = qi + 1 if qi < len(self.queues) - 1 else 0

    def allTasksComplete(self):
        return len(self.tasks) == 0