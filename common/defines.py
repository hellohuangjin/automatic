#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 基本类型定义模块 """

from enum import Enum


class InerException(Exception):
    """自定义异常类"""

    def __init__(self, msg, file_name=None):
        super(InerException, self).__init__(msg, file_name)
        self.msg = msg
        self.file = file_name

    def __str__(self):
        return "{file}: {msg}".format(file=self.file, msg=self.msg)


class TYPE(Enum):
    """ 命令类型 """
    net = 1  # 网络命令
    serial = 2  # 串口命令


class EVENT(Enum):
    """事件类型"""
    CHECK = 0
    CHECK_ERROR = 1
    PROGRAM_ERROR = 3
    INIT_COMPLETE = 4
    EVT_URGENCY = 5
    REG_PHONE = 6
    EVT_PAUSE = 7
    EVT_STOP = 8
    EVT_COMPLETE = 9
    EVT_START = 10
    EVT_CAMERA = 11
    SERIAL_CMD = 12
    CLEAR = 13



class LOGLEVER(Enum):
    """ 日志级别 """
    INFO = 0
    WARNING = 1
    ERROR = 2
