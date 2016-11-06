#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 通用类模块  """
import os
import sqlite3

from defines import LOGLEVER


class Logger(object):
    """自定义日志打印"""

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
        self.insert(LOGLEVER.INFO.value, msg)

    def warning(self, msg):
        """插入警告"""
        self.insert(LOGLEVER.WARNING.value, msg)

    def error(self, msg):
        """插入错误"""
        self.insert(LOGLEVER.ERROR.value, msg)

    def insert(self, lever, msg):
        """ 向数据库插入纪录 """
        sql = "INSERT INTO log (LEVER, MSG) VALUES(%d, '%s')" % (lever, msg)
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
