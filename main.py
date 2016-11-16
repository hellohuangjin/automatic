#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 主线程， UI """

import wx
from manager import EventManager

from common.defines import EVENT

from contract.camera_socket import CameraTools
from contract.board_serial import BoardTools
from reglib.detector import Detector
from view.window import MainFrame, ErrorFrame


class Window(object):

    def __init__(self):
        self.watcher = EventManager()
        self.watcher.start()
        self.watcher.attach_listener(EVENT.ERROR_PROGRAM, self.error)
        self.watcher.attach_listener(EVENT.EVT_SHUTDOWN, self.shutdown)
        self.app = wx.App()
        self.frame = MainFrame(self.watcher)

        self.socket = CameraTools(self.watcher)
        self.serial = BoardTools(self.watcher)

        self.detector = Detector(self.watcher)

    def start(self):
        self.socket.start_monitor()
        self.serial.start_monitor()
        self.detector.waiting_for_task()
        self.app.MainLoop()

    def error(self, msg):
        error = ErrorFrame(msg)
        self.watcher.publish(EVENT.EVT_SHUTDOWN, None)

    def shutdown(self):
        """关闭"""
        self.frame.Close()

if __name__ == '__main__':
    Window().start()
