#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 基本类型定义模块 """


class Enum(set):
    """自定义枚举常量"""
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


class InerException(Exception):
    """自定义异常类"""

    def __init__(self, msg, file_name=None):
        super(InerException, self).__init__(msg, file_name)
        self.msg = msg
        self.file = file_name

    def __str__(self):
        return "{file}: {msg}".format(file=self.file, msg=self.msg)


EVENT = Enum(['ERROR_HARDWARE',
              'ERROR_PROGRAM',
              'EVT_READY',
              'EVT_URGENCY',
              'EVT_GETPHONE',
              'EVT_GETBAR',
              'EVT_START',
              'EVT_PAUSE',
              'EVT_COMPLETE',
              'EVT_SHUTDOWN',
              'EVT_CMD',
              'EVT_CLEAR',
              'EVT_INFO'])

INFO = Enum(['EXPRESS', "BAR", "PHONE"])

LOGLEVER = Enum(['INFO', 'ERROR', 'WARNING'])
