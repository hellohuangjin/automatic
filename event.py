#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""异步事件管理器"""

from collections import defaultdict
from Queue import Queue, Empty
from threading import Thread

class EventManager(object):
    """事件管理器"""

    def __init__(self):
        self.__event_queue = Queue()
        self.__active = False
        self.__thread = Thread(target=self.__run)
        self.__handlers = defaultdict(list)

    def __run(self):
        """启动管理器"""
        while self.__active:
            try:
                event, msg = self.__event_queue.get(block=True, timeout=1)
                self.__event_process(event, msg)
            except Empty:
                pass

    def __event_process(self, event, msg):
        """事件处理"""
        if event in self.__handlers:
            for handler in self.__handlers[event]:
                if msg:
                    handler(msg)
                else:
                    handler()

    def start(self):
        """启动"""
        if not self.__active:
            self.__active = True
            self.__thread.start()

    def stop(self):
        """停止"""
        if self.__active:
            self.__active = False
            self.__thread.join()

    def add_listener(self, event, handler):
        """绑定事件监听"""
        if event not in self.__handlers:
            self.__handlers[event] = list()
        if handler not in self.__handlers[event]:
            self.__handlers[event].append(handler)
