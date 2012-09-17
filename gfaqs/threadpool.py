import threading
from Queue import Queue

class ThreadPool(object):
    def __init__(self, num_workers):
        self.task_queue = Queue(num_workers);
        for i in range(num_workers):
            Worker(self,task_queue)

    def add_task(self, fn, *args, **kwarg):
        task = (fn,args,kwargs)
        self.task_queue.put(task)

    def wait_finished(self):
        self.task_queue.join()

class Worker(threading.Thread):
    """ Runs tasks from thread pool"""
    def __init__(self, tasks):
        self.daemon= True
        self.tasks = tasks

    def run(self):
        while True:
            fn,args,kwargs = self.tasks.get()
            fn(args,kwargs)
            self.tasks.task_done()
