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

    camera = CameraTools(queue, 8500)
    camera.start_monitor()

    board = BoardTools(queue, 9600)
    board.start_monitor()

    app.MainLoop()

if __name__ == '__main__':
    main()
