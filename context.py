#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 全局数据 """

import os

from collections import defaultdict
from threading import Thread
from multiprocessing import Queue

from common.defines import LOGLEVER
from common.utils import Logger

from communication.server_request import Server


class _Watcher(Thread):
    """事件处理中间类"""

    def __init__(self):
        Thread.__init__(self)
        self._queue = Queue()
        self._event = defaultdict(list)
        self._log = log

    def original_cmd(self):
        return self._queue

    def attach(self, event_type, callback):
        """
        添加监听器
        :param event_type:事件类型
        :param callback:回调函数
        :return None
        """
        self._event[event_type].append(callback)

    def publish(self, event_type, msg):
        self._put_queue("NOTICE", event_type, msg)

    def log_info(self, msg):
        self._put_queue("LOG", LOGLEVER.INFO, msg)

    def log_warning(self, msg):
        self._put_queue("LOG", LOGLEVER.WARNING, msg)

    def log_error(self, msg):
        self._put_queue("LOG", LOGLEVER.ERROR, msg)

    def _put_queue(self, target, type, msg):
        self._queue.put((target, type, msg))

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

    def _logger(self, log_type, msg):
        """
        日志纪录事件
        :param log_type:日志级别
        :param msg:日志内容
        """
        if log_type == LOGLEVER.INFO:
            self._log.info(msg)
        elif log_type == LOGLEVER.WARNING:
            self._log.warning(msg)
        elif log_type == LOGLEVER.ERROR:
            self._log.error(msg)

    def run(self):
        """进程执行方法"""
        while True:
            target, type, msg= self._queue.get()
            if target == 'NOTICE':
                self._notice(type, msg)
            elif target == 'LOG':
                # self._logger(type, msg)
                pass

# 项目跟目录
PRJ_PATH = os.path.dirname(os.path.abspath(__file__))

# 自定义日志打印
log = Logger(PRJ_PATH)

# 全局http请求数据
server = Server()

# 全局事件监听器
watcher = _Watcher()
