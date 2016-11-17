#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""手机号识别库"""

import os
from threading import Thread
from Queue import Empty
from multiprocessing import Process, Queue

from common.defines import EVENT
from processor import Processor
from manager import PRJ_PATH

class RegProcess(Process):

    def __init__(self, inqueue, outqueue):
        super(RegProcess, self).__init__(self)
        self.inqueue = inqueue
        self.outqueue = outqueue
        self.active = False

    def run(self):
        """识别进程"""
        lang = os.path.join(PRJ_PATH, "source/")
        reg = Processor(lang)
        self.active = True
        while self.active:
            try:
                rect, name = self.inqueue.get(timeout=1)
            except Empty:
                pass
            else:
                path = "c:/img/"+name+".bmp"
                width, height, _, _ = rect.split(',')
                phone = reg.extract_phone(path, int(width), int(height))
                self.outqueue.put((name.split(",")[0], phone))



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
        self.watcher.attach_listener(EVENT.EVT_SHUTDOWN, self.stop)

    def waiting_for_task(self):
        """等待接受任务"""
        if not self._active:
            for _ in range(4):
                reg = RegProcess(self.inqueue, self.outqueue)
                reg.start()
                self.__processes.append(reg)

            self._active = True
            self._thread.start()

    def deliver(self, msg):
        """传递面单图像"""
        self.inqueue.put(msg)

    def __run(self):
        while self._active:
            msg = self.outqueue.get()
            self.watcher.publish(EVENT.EVT_GETPHONE, msg)

    def stop(self):
        """终止"""
        self._active = False
        for item in self.__processes:
            item.active = False
