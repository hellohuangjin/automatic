#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""手机号识别库"""

import os
from threading import Thread
from multiprocessing import Process, Queue, Pool

from common.defines import EVENT
# from processor import Processor
from manager import PRJ_PATH


def reg_process(inqueue, outqueue):
    """识别进程"""
    # lang = os.path.join(None, "source/")
    # reg_process = Processor(lang)
    while True:
        print "run"
        rect, name = inqueue.get()
        # path = "c:/img/"+name+".bmp"
        # width, height, _, _ = rect.split(',')
        # phone = reg_process.extract_phone(path, int(width), int(height))
        phone = "12345678901"
        outqueue.put((name.split(",")[0], phone))


class Detector(object):
    """收件人手机号识别类"""

    def __init__(self, watcher):
        self.watcher = watcher
        self.inqueue = Queue()
        self.outqueue = Queue()
        self._active = False
        self._thread = Thread(target=self.__run)
        self.__processes = list()

        self.watcher.attach_listener(EVENT.EVT_GETBAR, self.deliver)

    def waiting_for_task(self):
        if not self._active:
            for _ in range(4):
                process = Process(target=reg_process, args=(self.inqueue, self.outqueue,))
                process.start()
                self.__processes.append(process)

            self._active = True
            self._thread.start()

    def deliver(self, msg):
        print "deliver", msg
        self.inqueue.put(msg)

    def __run(self):
        while self._active:
            msg = self.outqueue.get()
            print "receive", msg
            # try:
                # msg = self.outqueue.get(block=True, timeout=1)
            # except Empty:
                # pass
            # else:
                # print msg

