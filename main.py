#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 主线程， UI """

import time
from multiprocessing import Process, Queue

from common.defines import TYPE

from context import watcher, log

from communication.camera_socket import CameraTools
from communication.board_serial import BoardTools

from gui.window import MainApp


class Communicate(Process):
    """ 通信子进程 """

    def __init__(self, args):
        """
        初始化
        :param mqueue: 文件队列
        :param name:端口名称
        """
        Process.__init__(self)
        mqueue, name, _watcher, _log = args
        self.inner_queue = Queue()
        self.socket = CameraTools(mqueue, 8500)
        self.serial = BoardTools(name, 9600)

    def send(self, cmd):
        """
        发送命令,cmd必需有两部分：命令内容，命令类型
        :param cmd:命令
        :return None
        """
        self.inner_queue.put(cmd)


    def run(self):
        """
        等待命令
        子线程，转发命令
        """
        self.socket.start_monitor()
        self.serial.start_monitor()
        while True:
            cmd = self.inner_queue.get()
            if cmd.target == TYPE.net:
                self.socket.send_command(cmd.content)
            if cmd.target == TYPE.serial:
                self.serial.send_command(cmd.content)


class Recognize(Process):
    """识别进程类"""

    def __init__(self, args):
        """
        初始化
        :param mqueue:文件队列
        :param name:进程名字
        :return None
        """
        Process.__init__(self)
        mqueue, name, _watcher, _log = args
        self.queue = mqueue
        self.name = name

    def run(self):
        """执行函数"""
        while True:
            img = self.queue.get()
            if img == 'quit':
                print "quit", self.name
                break
            print "start task", img, self.name
            time.sleep(0.5)

def main():
    """main函数"""

    app = MainApp()
    queue = Queue()
    for i in range(2):
        reg = Recognize(args=(queue, str(i), watcher, log,))
        reg.daemon = True
        reg.start()

    communicate = Communicate(args=(queue, "COM4", watcher, log,))
    communicate.daemon = True
    communicate.start()

    app.MainLoop()

if __name__ == '__main__':
    main()
