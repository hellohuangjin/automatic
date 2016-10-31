#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 全局数据 """

import os

from common.utils import Logger, RegisterTable

from communication.server_request import Server

# 项目跟目录
PRJ_PATH = os.path.dirname(os.path.abspath(__file__))

# 自定义日志打印
log = Logger(PRJ_PATH)

# 事件观察者
evt_watcher = RegisterTable()

# 全局http请求数据
server = Server()