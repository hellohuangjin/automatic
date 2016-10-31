#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""服务器通信"""

import time
import json
import hashlib

import requests

from common.utils import Singleton
from common.defines import InerException


class Server(object):
    """服务器通信工具类"""

    __metaclass__ = Singleton

    def __init__(self):
        self.base_url = "http://10.0.1.246:8888"
        self.url = {"login": "/cabzoo/szoo2/user/login",
                    "express": "/cabzoo/szoo2/express/list",
                    "batch": "/cabzoo/szoo2/batch/getlist",
                    "pre_add": "/cabzoo/szoo2/batch/pre_add",
                    'add': "/cabzoo/szoo2/batch/add"}
        self.logis = None
        self.uid = None
        self.sid = None
        self.express_list = None
        self.selected = dict()

    def login(self, name, password):
        """
        登录服务器
        :param name:用户名
        :param password:密码
        """
        url = self.base_url+self.url['login']
        params = {'ts': int(time.time()*1000), 'sn': "scanner", 'name': name, 'password': password}
        body = self.execute_request(url, self.gen_signer(params))
        self.sid = body['session']['sid']
        self.uid = body['id']
        return body['logis_list']

    def logout(self):
        """用户登出"""
        self.logis = None
        self.uid = None
        self.sid = None
        self.express_list = None
        self.clear_batch()

    def get_express_list(self):
        url = self.base_url+self.url['express']
        params = {'ts': int(time.time()*1000),
                  'sn': "scanner",
                  'logis_id': self.logis['id'],
                  'uid': self.uid,
                  'sid': self.sid}
        self.express_list = self.execute_request(url, self.gen_signer(params))

        return self.express_list

    def get_batch_list(self, express_id):
        self.selected["express_id"] = express_id
        url = self.base_url+self.url['batch']
        params = {'ts': int(time.time()*1000),
                  'sn': "scanner",
                  'logis_id': self.logis['id'],
                  'express_id': express_id,
                  'uid': self.uid,
                  'sid': self.sid}
        body = self.execute_request(url, self.gen_signer(params))
        return body

    def batch_pre_add(self):
        url = self.base_url+self.url['pre_add']
        if 'express_id' in self.selected:
            params = {'ts': int(time.time()*1000),
                      'sn': "scanner",
                      'express_id': self.selected['express_id'],
                      'logis_id': self.logis['id'],
                      'uid': self.uid,
                      'sid': self.sid}

            body = self.execute_request(url, self.gen_signer(params))
        else:
            body = None
        return body

    def batch_add(self, batch_date, seq_no):
        url = self.base_url+self.url['add']
        params = {'ts': int(time.time()*1000),
                  'sn': "scanner",
                  'batch_date': batch_date,
                  'seq_no': seq_no,
                  'express_id': self.selected['express_id'],
                  'logis_id': self.logis['id'],
                  'uid': self.uid,
                  'sid': self.sid}
        body = self.execute_request(url, self.gen_signer(params))
        return body

    def clear_batch(self):
        self.selected = dict()


    @staticmethod
    def gen_signer(params):
        """
        产生服务器签名
        :param name:用户名
        :param password:密码
        """
        secret = "SFPD0afjaLN?SFl0ad$?*&+=(*#21#$K"
        params['sign_type'] = 'MD5'
        param_list = sorted(params.items(), key=lambda item: item[0])
        code_string = ""

        for key, value in param_list:
            code_string += "{key}={value}&".format(key=key, value=value)
        code_string += "secret=%s" % secret
        sign = hashlib.md5(code_string).hexdigest()
        params['sign'] = sign
        return params

    @staticmethod
    def execute_request(url, params=None):
        """
        执行http请求
        :param url: 请求地址
        :param params: 请求参数
        :return: None
        """
        try:
            rsp = requests.post(url, data=params)
        except requests.RequestException as e:
            # 使用全局数据，避免循环导入
            from context import log
            log.error(str(e))
            raise InerException("http request error", __file__)
        else:
            content = json.loads(rsp.content)
            return content['body']
