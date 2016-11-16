#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
python socket 通信模块
"""
import socket
import threading

from common.defines import EVENT, INFO, InerException


class CameraTools(object):
    """ 视觉系统通信工具类 """

    def __init__(self, watcher):
        """
        初始化
        :param port:端口
        :return None
        """
        self.watcher = watcher
        self.port = 8500
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.task = None
        self._active = False

    def start_monitor(self):
        """ 启动tcp监听 """
        if not self.task:
            self._active = True
            self._connect()
            self.task = threading.Thread(target=self.receive)
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
        if cmd == 'Ready':
            pass
        else:
            check, pos, name = cmd.split(";")
            if check == '0':
                self.watcher.publish(EVENT.EVT_INFO, (INFO.BAR, 1, 0))
            else:
                self.watcher.publish(EVENT.EVT_GETBAR, (pos, name))
                self.watcher.publish(EVENT.EVT_INFO, (INFO.BAR, 1, 1))

    def receive(self):
        """ 消息接收线程 """
        while self._active:
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
            self.watcher.publish(EVENT.ERROR_PROGRAM, "socket connect error")
            raise InerException("socket connect error", __file__)
