#!/usr/bin/env python3

import threading, cv2, os, queue

class QueueThread:
    def __init__(self):
        self.queue = []
        self.full = threading.Semaphore(0)
        self.empty = threading.Semaphore(10)
        self.lock = threading.Lock()

    def enqueue(self, item):
        self.empty.acquire()
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()
        self.full.release()

    def dequeue(self):
        self.full.acquire()
        self.lock.acquire()
        frame = self.queue.pop(0)
        self.lock.release()
        self.empty.release()
        return frame
