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
        watcher = EventManager()
        watcher.start()
        watcher.attach_listener(EVENT.ERROR_PROGRAM, self.error)
        self.app = wx.App()
        self.frame = MainFrame(watcher)

        self.socket = CameraTools(watcher)
        self.serial = BoardTools(watcher)

        self.detector = Detector(watcher)

    def start(self):
        self.socket.start_monitor()
        self.serial.start_monitor()
        self.detector.waiting_for_task()
        self.app.MainLoop()

    def error(self, msg):
        error = ErrorFrame(msg)

if __name__ == '__main__':
    Window().start()
