#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
python socket 通信模块
"""
import socket
import threading

from context import log, watcher

from common.defines import EVENT, InerException
from common.utils import Singleton


class CameraTools(object):
    """ 视觉系统通信工具类 """

    __metaclass__ = Singleton

    def __init__(self, mqueue, port):
        """
        初始化
        :param port:端口
        :return None
        """
        self.queue = mqueue
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.task = None

    def start_monitor(self):
        """ 启动tcp监听 """
        if not self.task:
            self._connect()
            self.task = threading.Thread(target=self.receive)
            self.task.setDaemon(True)
            self.task.start()

    def send_command(self, command):
        """
        发送命令
        :command: 命令内容
        :return: True or False
        """
        try:
            self.server.sendall(command)
        except socket.error:
            self._reconnect()
        finally:
            self.server.sendall(command)

    def decode_cmd(self, cmd):
        """
        命令解析
        :cmd:命令内容
        """
        check, pos, name = cmd.split(";")
        self.queue.put(name)
        watcher.notice(EVENT.EVT_CAMERA, name)

    def receive(self):
        """ 消息接收线程 """
        while True:
            cmd = self.server.recv(64)
            if cmd == '':
                self._reconnect()
            else:
                self.decode_cmd(cmd.strip())

    def _reconnect(self):
        """ 重连函数 """
        self.server.close()
        return self._connect()

    def _connect(self):
        """ 连接socket """
        try:
            self.server.connect(("localhost", self.port))
        except socket.error:
            log.error("socket connect error")
            watcher.notice(EVENT.PROGRAM_ERROR, "socket connect error")
            raise InerException("socket connect error", __file__)
