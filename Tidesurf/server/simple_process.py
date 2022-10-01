from multiprocessing import Process, Queue
import time
import json
QUEUE = Queue()

def producer(queue):
    while(True):
        queue.put(str(time.time()))
        time.sleep(1)

def consumer(queue):
    result = []
    cur = 0
    while(True):
        s = queue.get()
        if s:
            result.append(s)
            if (len(result) == 10):
                with open(f"./{cur}.json", "w") as f:
                    f.write(json.dumps(result))
                    cur += 1
                    result = []

def start_job():
    global QUEUE
    p1 = Process(target=consumer, args=(QUEUE,))
    p2 = Process(target=producer, args=(QUEUE,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
