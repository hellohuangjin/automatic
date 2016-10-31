#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 主线程， UI """

import time
from multiprocessing import Process, Queue

from common.defines import TYPE

from communication.camera_socket import CameraTools
from communication.board_serial import BoardTools

from gui.window import MainApp


class Communicate(object):
    """ 通信子进程 """

    def __init__(self, mqueue, name="COM3"):
        """
        初始化
        :param mqueue: 文件队列
        :param name:端口名称
        """
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


def communicate_process(ins):
    """
    等待命令
    子线程，转发命令
    """
    ins.socket.start_monitor()
    ins.serial.start_monitor()
    while True:
        cmd = ins.inner_queue.get()
        if cmd.target == TYPE.net:
            ins.socket.send_command(cmd.content)
        if cmd.target == TYPE.serial:
            ins.serial.send_command(cmd.content)


class Recognize(Process):
    """识别进程类"""

    def __init__(self, mqueue, name):
        """
        初始化
        :param mqueue:文件队列
        :param name:进程名字
        :return None
        """
        Process.__init__(self)
        self.queue = mqueue
        self.name = name

def recognize_process(ins):
    """执行函数"""
    while True:
        img = ins.queue.get()
        if img == 'quit':
            print "quit", ins.name
            break
        print "start task", img, ins.name
        time.sleep(0.5)

def main():
    """main函数"""

    app = MainApp()
    queue = Queue()
    for i in range(2):
        reg = Recognize(queue, str(i))
        proccess = Process(target=recognize_process, args=(reg,))
        proccess.daemon = True
        proccess.start()

    com = Communicate(queue)
    pro = Process(target=recognize_process, args=(com,))
    pro.daemon = True
    pro.start()
    app.MainLoop()

if __name__ == '__main__':
    main()
