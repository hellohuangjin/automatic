#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 主线程， UI """
import os
from multiprocessing import Process, Queue, Manager

from processor import Processor

from context import watcher, PRJ_PATH

from common.defines import EVENT
from communication.camera_socket import CameraTools
from communication.board_serial import BoardTools

from gui.window import Window


class Recognize(Process):
    """识别进程类"""

    def __init__(self, queue, notice):
        """
        初始化
        :param mqueue:文件队列
        :param name:进程名字
        :return None
        """
        Process.__init__(self)
        self.queue = queue
        self.notice = notice

    def run(self):
        """执行函数"""
        lang = os.path.join(PRJ_PATH, "source/")
        reg_process = Processor(lang)
        while True:
            rect, name = self.queue.get()
            path = "c:/img/"+name+".bmp"
            width, height, _, _ = rect.split(',')
            phone = reg_process.extract_phone(path, int(width), int(height))
            phone = "12345678901"
            self.notice.put(("NOTICE", EVENT.REG_PHONE, (name.split(",")[0], phone)))


def main():
    """main函数"""

    app = Window()
    queue = Queue()

    watcher.daemon = True
    watcher.start()

    for _ in range(2):
        reg = Recognize(queue, watcher.original_cmd())
        reg.daemon = True
        reg.start()

    camera = CameraTools(queue, 8500)
    camera.start_monitor()

    board = BoardTools()
    board.start_monitor()

    app.show()

if __name__ == '__main__':
    main()
