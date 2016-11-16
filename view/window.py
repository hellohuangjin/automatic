#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 主窗口 """

import os

import wx
import wx.grid

from common.defines import EVENT, INFO

from contract.server_request import Server

from manager import PRJ_PATH
from view.custome import LabelTable, ListTable, Button
from view.diolag import SelectDiolag, ImageExplore, LoginDiolag


class MainFrame(wx.Frame):
    """ 主界面 """

    def __init__(self, watcher):
        """
        如果父元素为None(默认为None, 必须传入),则该frame作为顶级元素，
        title为窗口标题，可以不设置。
        :param watcher:异步事件监听
        :return None
        """

        style = wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX |
                                          wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, None, id=wx.ID_ANY, style=style)

        self.status_panel = StatusPanel(self)
        self.info_panel = InfoPanel(self)
        self.ctrl_panel = CtrlPanel(self)
        self.list_panel = ListPanel(self)

        self.ctrl_panel.watcher = watcher

        self.SetBackgroundColour((207, 207, 207))

        left = wx.BoxSizer(wx.VERTICAL)

        left.Add(self.status_panel, 0, wx.EXPAND)
        left.Add(self.info_panel, 0, wx.EXPAND | wx.TOP, 30)
        left.Add(self.ctrl_panel, 0, wx.EXPAND | wx.TOP, 30)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left, wx.ID_ANY, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, 30)
        sizer.Add(self.list_panel, wx.ID_ANY, wx.EXPAND | wx.RIGHT | wx.TOP | wx.LEFT, 30)

        self.SetSizer(sizer)

        self._init_event(watcher)

        self.Show(True)

        self.ShowFullScreen(True)

    def _init_event(self, watcher):

        # 列表view事件
        watcher.attach_listener(EVENT.EVT_GETPHONE, self.list_panel.new_data)
        watcher.attach_listener(EVENT.EVT_COMPLETE, self.list_panel.clear)

        # 状态展示view事件
        watcher.attach_listener(EVENT.EVT_START, self.status_panel.change_status)
        watcher.attach_listener(EVENT.EVT_PAUSE, self.status_panel.change_status)
        watcher.attach_listener(EVENT.EVT_URGENCY, self.status_panel.change_status)
        watcher.attach_listener(EVENT.EVT_COMPLETE, self.status_panel.change_status)

        # 信息展示view事件
        watcher.attach(EVENT.EVT_GETBAR, self.info_panel.change_img)
        watcher.attach_listener(EVENT.EVT_INFO, self.info_panel.update_info)
        watcher.attach_listener(EVENT.EVT_COMPLETE, self.info_panel.clear_info)

        # 控制view事件
        watcher.attach_listener(EVENT.EVT_URGENCY, self.ctrl_panel.urgency_event)
        watcher.attach_listener(EVENT.EVT_CLEAR, self.ctrl_panel.urgency_event)


class ListPanel(wx.Panel):
    """ panel """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(476, 600))
        self.SetBackgroundColour((207, 207, 207))
        self.table = ListTable(self)
        self.table.SetSize((476, 700))
        self.table.set_label(["id", u"运单号", u"手机号"])
        self.index = 0
        self.data = list()

    def new_data(self, msg):
        """ 添加新纪录 """
        self.index += 1
        if len(self.data) > 12:
            self.data.pop()
        bar_code, phone = msg
        self.data.insert(0, (str(self.index), bar_code, phone))
        self.table.set_data(self.data)

    def clear(self, _):
        self.data = list()
        self.index = 0
        self.table.clear()


class StatusPanel(wx.Panel):
    """状态展示panel """

    def __init__(self, parent):
        super(StatusPanel, self).__init__(parent)
        img_url = os.path.join(PRJ_PATH, "source/img/ready.jpg")
        image = wx.Image(img_url, wx.BITMAP_TYPE_JPEG).Scale(800, 350)
        self.static_img = wx.StaticBitmap(
            self, wx.ID_ANY, image.ConvertToBitmap(), size=(800, 350))

        self.ClearBackground()

    def change_status(self, msg):
        """
        状态改变监听事件
        :param msg: 事件名称
        :return: None
        """
        img_url = None
        if msg == "pause":
            img_url = os.path.join(PRJ_PATH, 'source/img/pause.jpg')
        elif msg == "urgency":
            img_url = os.path.join(PRJ_PATH, 'source/img/uergency.jpg')
        elif msg == "complete":
            img_url = os.path.join(PRJ_PATH, 'source/img/ready.jpg')
        elif msg == 'start':
            img_url = os.path.join(PRJ_PATH, 'source/img/start.jpg')

        image = wx.Image(img_url, wx.BITMAP_TYPE_JPEG).Scale(800, 350)
        self.static_img.SetBitmap(image.ConvertToBitmap())


class InfoPanel(wx.Panel):
    """信息展示panel"""

    def __init__(self, parent):
        super(InfoPanel, self).__init__(parent)
        self.img = None
        self.SetBackgroundColour((207, 207, 207))
        self.express_img = wx.BitmapButton(
            self, wx.ID_ANY, wx.NullBitmap, size=(300, 246))
        self.img = self.express_img
        self.info = [0, 0, 0, 0]

        labels = [u"快递公司", u"接驳批次", u"快件总数", u"接驳数", u"手机号识别数", u"异常件数"]

        self.table = LabelTable(self)
        self.table.SetSize((450, 246))
        self.table.set_label(labels)

        self.express_img.Bind(wx.EVT_BUTTON, self.img_explore)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.table, wx.ID_ANY, wx.EXPAND)
        sizer.Add(self.express_img, wx.ID_ANY, wx.EXPAND | wx.LEFT, 50)

        self.SetSizer(sizer)

    def update_info(self, msg):
        """更新表"""
        type_ = msg[0]
        if type_ == INFO.EXPRESS:
            for row, value in enumerate(msg[1:]):
                self.table.set_cell(row, value)
        elif type_ == INFO.BAR:
            self.info[0] += msg[1]
            self.info[1] += msg[2]
            self.table.set_cell(2, str(self.info[0]))
            self.table.set_cell(3, str(self.info[1]))
        elif type_ == INFO.PHONE:
            self.info[2] += msg[1]
            self.info[3] += msg[2]
            self.table.set_cell(4, str(self.info[2]))
            self.table.set_cell(5, str(self.info[3]))

    def clear_info(self):
        """清除信息表"""
        info = [u'尚未接驳', u'尚未接驳', u'0', u'0', u'0', u'0']
        self.table.set_data(info)
        self.info = [0, 0, 0, 0]

    def change_img(self, name):
        """
        变更显示快递图片
        :param name:图片名称
        """
        url = "c:/img/" + name + ".bmp"
        img = wx.Image(url, wx.BITMAP_TYPE_BMP)
        self.img.SetBitmap(img.ConvertToBitmap())

    def img_explore(self, _):
        """
        图片点击时触发浏览大图
        :param event:事件类型
        :return None
        """

        dlg = ImageExplore(self, u"快递面单")
        self.img = dlg
        dlg.SetBitmap(wx.NullBitmap)
        dlg.SetPosition((478, 150))
        dlg.ShowModal()
        self.img = self.express_img
        dlg.Destroy()


class CtrlPanel(wx.Panel):
    """ list panel  """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.key = [0, 0, 0, 1, 0]
        self.SetBackgroundColour((207, 207, 207))
        self.watcher = None
        self.urgency = False
        self.server = Server()
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        start = Button(self, text=u"开始接驳", size=(120, 52), colour='green')
        pause = Button(self, u"暂停接驳", (120, 52), 'yellow')
        complete = Button(self, u"完成接驳", (120, 52), 'green')
        shoutdown = Button(self, u"关机", (120, 52), 'red')
        self.login_btn = Button(self, u"登录", (120, 52), 'white')

        sizer.Add(start, 0, wx.EXPAND)
        sizer.Add(pause, 0, wx.EXPAND | wx.LEFT, 50)
        sizer.Add(complete, 0, wx.EXPAND | wx.LEFT, 50)
        sizer.Add(shoutdown, 0, wx.EXPAND | wx.LEFT, 50)
        sizer.Add(self.login_btn, 0, wx.EXPAND | wx.LEFT, 50)

        self.Bind(wx.EVT_BUTTON, self.start, start)
        self.Bind(wx.EVT_BUTTON, self.pause, pause)
        self.Bind(wx.EVT_BUTTON, self.complete, complete)
        self.Bind(wx.EVT_BUTTON, self.shoutdown, shoutdown)
        self.Bind(wx.EVT_BUTTON, self.login, self.login_btn)

        self.SetSizer(sizer)

    def urgency_event(self, msg):
        """ 紧急情况，禁止所有按钮 """
        if msg == 'urgency':
            self.urgency = True
        elif msg == 'clear':
            self.urgency = False

    def login(self, _):
        """
        登录菜单
        """
        if self.urgency:
            return
        if self.server.uid is None:
            login = LoginDiolag(self)
            login.SetPosition((550, 250))
            login.ShowModal()
            if self.server.uid:
                self.login_btn.SetLabel(u"注销")
            login.Destroy()
        else:
            self.server.logout()
            self.login_btn.SetLabel(u"登录")

    def start(self, _):
        """
        设备启动菜单时间处理器
        点击启动菜单时调用该函数
        """
        if self.urgency:
            return
        all_key_in = "batch_id" in self.server.selected and "express_id" in self.server.selected
        if not all_key_in:
            express_list = self.server.get_express_list()
            select = SelectDiolag(self, u"选择窗口", express_list)
            select.SetPosition((400, 200))
            select.ShowModal()
            all_key_in = "batch_id" in self.server.selected and "express_id" in self.server.selected
            if all_key_in:
                express, batch = select.get_select_info()
                self.watcher.publish(EVENT.EVT_CMD, "AA05start")
                self.watcher.publish(EVENT.EVT_START, "start")
                self.watcher.publish(EVENT.EVT_INFO, (INFO.EXPRESS, express, batch))
            else:
                self.server.clear_batch()
            select.Destroy()
        else:
            self.watcher.publish(EVENT.EVT_CMD, "AA05start")
            self.watcher.publish(EVENT.EVT_START, "start")

    def pause(self, _):
        """ 暂停 """
        if self.urgency:
            return
        self.watcher.publish(EVENT.EVT_CMD, "AA04stop")
        self.watcher.publish(EVENT.EVT_PAUSE, 'pause')

    def complete(self, _):
        """ 完成接驳 """
        if self.urgency:
            return
        self.server.clear_batch()
        self.watcher.publish(EVENT.EVT_COMPLETE, 'complete')
        self.watcher.publish(EVENT.EVT_CMD, "AA04stop")
        self.watcher.publish(EVENT.EVT_INFO, None)

    def shoutdown(self, _):
        """ 关机 """
        self.watcher.publish(EVENT.EVT_CMD, "AA08shutdown")
        exit(0)
