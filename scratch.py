from redis import Redis
from rq import Queue
import TaskManager
import time

tm = TaskManager.TaskManager()