# -*- coding: utf-8 -*-
"""
A threadpool implementation
http://en.wikipedia.org/wiki/Thread_pool_pattern
"""
import threading
from Queue import Queue

class ThreadPool(object):
    def __init__(self, num_workers):
        self.task_queue = Queue(num_workers);
        self.workers = []
        for i in range(num_workers):
            w = Worker(self.task_queue)
            self.workers.append(w)

    def add_task(self, fn, *args, **kwargs):
        task = (fn,args,kwargs)
        self.task_queue.put(task)

    def wait_finished(self):
        self.task_queue.join()

class Worker(threading.Thread):
    """ Runs tasks from thread pool"""
    def __init__(self, tasks):
        super(Worker,self).__init__()
        self.daemon= True
        self.tasks = tasks
        self.start()

    def run(self):
        while True:
            fn,args,kwargs = self.tasks.get()
            fn(*args,**kwargs)
            self.tasks.task_done()
