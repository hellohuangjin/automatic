#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 内部串口通信 """

import threading
import serial

from context import log, evt_watcher

from common.defines import EVENT, InerException
from common.utils import Singleton

EXCEPTION = {"NORMAL": 0x0000, "board": 0x0001, "visor": 0x0002, "485": 0x0004, "conveyor": 0x0008}


class BoardTools(object):
    """ 通过串口发送接收命令 """

    __metaclass__ = Singleton

    def __init__(self, port, baudrate):
        """
        初始化函数
        :param port:端口
        :param baudrate:波特率
        :return None
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.task = None

    def start_monitor(self):
        """
        启动串口监听
        """
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
            self.serial.write(command)
        except serial.SerialException:
            self._connect()

    def decode_cmd(self, content):
        """
        解析命令
        :param content:命令内容
        :return None
        """
        cm_type = content[:2]
        length = content[2:4]
        cmd = content[4:length]

        if cm_type == 'AA':
            if cmd == 'urgency':
                evt_watcher.notice(EVENT.EVT_URGENCY, None)
        elif cm_type == 'AB':
            for key, code in EXCEPTION:
                if is_exception(cmd, code):
                    print "exception", key

    def receive(self):
        """ 消息接收线程 """
        while True:
            cmd = self.serial.readline()
            self.decode_cmd(cmd)

    def _reconnect(self):
        """重连"""
        self.serial.close()
        self._connect()

    def _connect(self):
        """
        串口连接
        """
        try:
            self.serial = serial.Serial(self.port, self.baudrate)
        except serial.SerialException:
            log.error("serial connect error")
            raise InerException("serial content error", __file__)


def is_exception(content, key):
    """判断异常种类"""
    return True if content&key == key else False
