#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 全局数据 """

import os

from collections import defaultdict
from threading import Thread
from Queue import Queue, Empty

from common.defines import EVENT

class EventManager(Thread):
    """事件处理中间类"""

    def __init__(self):
        Thread.__init__(self)
        self._queue = Queue()
        self._event = defaultdict(list)
        self.__active = False

        self._event[EVENT.EVT_SHUTDOWN].append(self.stop)

    def attach_listener(self, event_type, callback):
        """
        添加监听器
        :param event_type:事件类型
        :param callback:回调函数
        :return None
        """
        self._event[event_type].append(callback)

    def publish(self, event_type, msg):
        """
        发布通知
        :param event_type:通知类型
        :param msg:通知内容
        """
        self._queue.put((event_type, msg))

    def _notice(self, event_type, msg=None):
        """
        发布事件通知
        :param event_type:事件类型
        :param msg:消息
        :return None
        """
        for callback in self._event[event_type]:
            if msg is None:
                callback()
            else:
                callback(msg)

    def run(self):
        """进程执行方法"""
        self.__active = True
        while self.__active:
            try:
                type_, msg = self._queue.get(block=True, timeout=1)
            except Empty:
                pass
            else:
                self._notice(type_, msg)


    def stop(self):
        """终止"""
        self.__active = False


# 项目跟目录
PRJ_PATH = os.path.dirname(os.path.abspath(__file__))
