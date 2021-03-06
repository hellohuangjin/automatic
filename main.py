#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 主线程， UI """
import os
import time
from multiprocessing import Process, Queue

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
            start_time = time.time()
            path = "c:/img/"+name+".bmp"
            width, height, _, _ = rect.split(',')
            phone = reg_process.extract_phone(path, int(width), int(height))
            print "phone: {0}; time: {1}".format(phone, time.time()-start_time)
            self.notice.put(("NOTICE", EVENT.REG_PHONE, (name.split(",")[0], phone)))


def main():
    """main函数"""

    app = Window()
    queue = Queue()

    watcher.start()

    for _ in range(4):
        reg = Recognize(queue, watcher.original_cmd())
        reg.start()

    camera = CameraTools(queue, 8500)
    camera.start_monitor()

    board = BoardTools()
    board.start_monitor()

    app.show()

if __name__ == '__main__':
    main()
