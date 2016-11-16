#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 内部串口通信 """

import threading
import serial

from common.defines import EVENT, InerException


class BoardTools(object):
    """ 通过串口发送接收命令 """

    def __init__(self, watcher):
        """
        初始化函数
        :param port:端口
        :param baudrate:波特率
        :return None
        """
        self.port = "COM5"
        self.baudrate = 115200
        self.serial = None
        self.task = None
        self.watcher = watcher
        self.watcher.attach_listener(EVENT.EVT_CMD, self._send_command)

    def start_monitor(self):
        """
        启动串口监听
        """
        if not self.task:
            self._connect()
            self.task = threading.Thread(target=self.receive)
            self.task.setDaemon(True)
            self.task.start()

    def _send_command(self, command):
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
        length = int(content[2:4])
        cmd = content[4:length+4]

        if cm_type == 'AB':
            if cmd == 'urgency':
                self.watcher.publish(EVENT.EVT_URGENCY, cmd)
            elif cmd == 'clear':
                self.watcher.publish(EVENT.CLEAR, cmd)

    def receive(self):
        """ 消息接收线程 """
        while True:
            cmd = self.serial.readline()
            self.decode_cmd(cmd.strip())

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
            self.watcher.publish(EVENT.ERROR_PROGRAM, "serial connect error")
            raise InerException("serial content error", __file__)
