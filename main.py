#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 主线程， UI """

import time
from multiprocessing import Process, Queue

import wx
from context import watcher

from common.defines import EVENT
from communication.camera_socket import CameraTools
from communication.board_serial import BoardTools

from gui.window import MainFrame


class Recognize(Process):
    """识别进程类"""

    def __init__(self, queue):
        """
        初始化
        :param mqueue:文件队列
        :param name:进程名字
        :return None
        """
        Process.__init__(self)
        self.queue = queue

    def run(self):
        """执行函数"""
        while True:
            rect, name = self.queue.get()
            print "img", name
            watcher.publish(EVENT.REG_PHONE, (name.split(",")[0], "15810305071"))
            time.sleep(0.5)


def main():
    """main函数"""
    app = wx.App()

    queue = Queue()

    watcher.daemon = True
    watcher.start()

    for i in range(2):
        reg = Recognize(queue)
        reg.daemon = True
        reg.start()

    camera = CameraTools(queue, 8500)
    camera.start_monitor()

    # board = BoardTools(intermediary, 9600)
    # board.start_monitor()

    frame = MainFrame(parent=None, title=u"自动分拣")
    frame.ShowFullScreen(True)

    app.MainLoop()

if __name__ == '__main__':
    main()
