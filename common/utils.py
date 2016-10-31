#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 通用类模块  """
import os
import sqlite3
from collections import defaultdict

from defines import LOGLEVER


class Singleton(type):
    """单例元类"""
    _inst = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._inst:
            cls._inst[cls] = super(Singleton, cls).__call__(*args)
        return cls._inst[cls]


class RegisterTable(object):
    """注册事件类"""

    __metaclass__ = Singleton

    def __init__(self):
        self.event = defaultdict(list)

    def depatch(self, event_type, callback):
        """
        移除监听器
        :param event_type:事件类型
        :param callback:回调函数
        :return None
        """
        if event_type in self.event:
            self.event[event_type].remove(callback)

    def attach(self, event_type, callback):
        """
        添加监听器
        :param event_type:事件类型
        :param callback:回调函数
        :return None
        """
        self.event[event_type].append(callback)

    def notice(self, event_type, msg=None):
        """
        发布事件通知
        :param event_type:事件类型
        :param msg:消息
        :return None
        """
        for callback in self.event[event_type]:
            if msg is None:
                callback()
            else:
                callback(msg)


class Logger(object):
    """自定义日志打印"""

    __metaclass__ = Singleton

    def __init__(self, prj_path):
        dbpath = os.path.join(prj_path, 'source/log/log.db')
        self.conn = sqlite3.connect(dbpath)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        if self._check_table():
            print True
            self._create_table()


    def info(self, msg):
        """插入info"""
        self.insert(LOGLEVER.info.value, msg)

    def warning(self, msg):
        """插入警告"""
        self.insert(LOGLEVER.warning.value, msg)

    def error(self, msg):
        """插入错误"""
        self.insert(LOGLEVER.error.value, msg)

    def insert(self, lever, msg):
        """ 向数据库插入纪录 """
        sql = "INSERT INTO log (LEVER, MSG) VALUES(%d, '%s')" %(lever, msg)
        print "insert", sql
        self.execute(sql)

    def execute(self, sql):
        """ 执行sql语句 """
        self.cursor.execute(sql)
        self.conn.commit()

    def _check_table(self):
        """检查表是否已经存在"""
        sql = "SELECT COUNT(*) FROM sqlite_master where type='table' and name='log'"
        self.execute(sql)
        result = self.cursor.fetchall()
        return result[0][0] == 0

    def _create_table(self):
        """创建表"""
        sql = "CREATE TABLE log( \
                                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                                lever INT8 NOT NULL, \
                                msg TEXT NOT NULL, \
                                time TIMESTAMP NOT NULL DEFAULT (datetime('now', 'localtime')))"
        self.execute(sql)

    def __del__(self):
        """对象销毁"""
        self.conn.close()
