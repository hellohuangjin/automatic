#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""手机号识别库"""

import os
from threading import Thread
from multiprocessing import Process, Queue, Pool

from common.defines import EVENT
# from processor import Processor
from manager import PRJ_PATH


class RegProcess(Process):
    """识别进程"""

    def __init__(self, inqueue, outqueue):
        super(RegProcess, self).__init__(self)
        self._active = False
        self._inqueue = inqueue
        self._outqueue = outqueue

    def run(self):
        """识别进程"""
        self._active = True
        lang = os.path.join(PRJ_PATH, "source/")
        # reg = Processor(lang)
        while self._active:
            rect, name = self._inqueue.get()
            path = "c:/img/"+name+".bmp"
            width, height, _, _ = rect.split(',')
            # phone = reg.extract_phone(path, int(width), int(height))
            phone = '15201121726'
            self._outqueue.put((name.split(",")[0], phone))

    def stop(self):
        """终止"""
        self._active = False


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
            item.stop()
