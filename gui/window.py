#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 主窗口 """

import os

import wx
import wx.grid

from common.defines import EVENT

from context import PRJ_PATH, server, watcher
from gui.custome import LabelTable, ListTable, Button
from gui.diolag import SelectDiolag, ImageExplore, LoginDiolag


class Window(object):
    """GUI"""

    def __init__(self):

        self.app = wx.App()
        self.frame = MainFrame(None)
        watcher.attach(EVENT.PROGRAM_ERROR, self.program_error)

    def program_error(self, msg):
        """程序启动错误监听"""
        self.frame = ErrorFrame(parent=None, msg=msg)
        print "error", msg

    def show(self):
        """显示界面"""
        self.frame.ShowFullScreen(True)
        self.app.MainLoop()


class ErrorFrame(wx.Frame):
    """错误信息界面"""

    def __init__(self, parent, msg=None):
        wx.Frame.__init__(self, parent, title=u"程序错误")


class MainFrame(wx.Frame):
    """ 主界面 """

    def __init__(self, parent):
        """
        如果父元素为None(默认为None, 必须传入),则该frame作为顶级元素，
        title为窗口标题，可以不设置。
        :param parent:父元素
        :param title:窗口标题
        :return None
        """

        style = wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX |
                                          wx.MAXIMIZE_BOX)
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=u"自动分拣",
            size=(1366, 768),
            style=style)

        self.status_panel = StatusPanel(self)
        self.info_panel = InfoPanel(self)
        self.ctrl_panel = CtrlPanel(self)
        self.list_panel = ListPanel(self)

        left = wx.BoxSizer(wx.VERTICAL)

        left.Add(self.status_panel, 0, wx.EXPAND)
        left.Add(self.info_panel, 0, wx.EXPAND | wx.TOP, 30)
        left.Add(self.ctrl_panel, 0, wx.EXPAND | wx.TOP, 30)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(left, wx.ID_ANY, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM,
                  30)
        sizer.Add(self.list_panel, wx.ID_ANY, wx.EXPAND | wx.RIGHT | wx.TOP |
                  wx.LEFT, 30)

        self.SetSizer(sizer)
        sizer.Fit(self)

        self.Show(True)


class ListPanel(wx.Panel):
    """ panel """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size=(476, 600))
        self.table = ListTable(self)
        self.table.SetSize((476, 600))
        self.table.set_label(["id", u"运单号", u"手机号"])
        self.index = 0
        self.data = list()
        watcher.attach(EVENT.REG_PHONE, self.new_data)

    def new_data(self, msg):
        """ 添加新纪录 """
        self.index += 1
        if len(self.data) > 10:
            self.data.pop()
        bar_code, phone = msg
        self.data.insert(0, (str(self.index), bar_code, phone))
        self.table.set_data(self.data)


class StatusPanel(wx.Panel):
    """状态展示panel """

    def __init__(self, parent):
        super(StatusPanel, self).__init__(parent)
        img_url = os.path.join(PRJ_PATH, "source/img/ready.png")
        image = wx.Image(img_url, wx.BITMAP_TYPE_PNG).Scale(800, 350)
        self.static_img = wx.StaticBitmap(
            self, wx.ID_ANY, image.ConvertToBitmap(), size=(800, 350))
        watcher.attach(EVENT.EVT_PAUSE, self.change_status)
        self.ClearBackground()

    def change_status(self, msg):
        """
        状态改变监听事件
        :param msg: 事件名称
        :return: None
        """
        img_url = None
        if msg == "pause":
            img_url = os.path.join(PRJ_PATH, 'source/img/pause.png')
        elif msg == "urgency":
            img_url = os.path.join(PRJ_PATH, 'source/img/uergency.png')
        elif msg == "complete":
            img_url = os.path.join(PRJ_PATH, 'source/img/ready.png')

        image = wx.Image(img_url, wx.BITMAP_TYPE_PNG).Scale(800, 350)
        self.static_img.SetBitmap(image.ConvertToBitmap())


class InfoPanel(wx.Panel):
    """信息展示panel"""

    def __init__(self, parent):
        super(InfoPanel, self).__init__(parent)
        self.img = None

        self.express_img = wx.BitmapButton(
            self, wx.ID_ANY, wx.NullBitmap, size=(300, 246))
        self.img = self.express_img

        labels = [u"快递公司", u"接驳批次", u"快件总数", u"接驳数", u"手机号识别数", u"异常件数"]

        self.table = LabelTable(self)
        self.table.SetSize((550, 246))
        self.table.set_label(labels)
        watcher.table_update = self.table.set_data

        self.express_img.Bind(wx.EVT_BUTTON, self.img_explore)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.table, wx.ID_ANY, wx.EXPAND)
        sizer.Add(self.express_img, wx.ID_ANY, wx.EXPAND | wx.LEFT, 50)

        watcher.attach(EVENT.EVT_CAMERA, self.change_img)

        self.SetSizer(sizer)

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
        dlg.SetBitmap(wx.BitmapFromImage(self.img))
        dlg.SetPosition((478, 150))
        dlg.ShowModal()
        self.img = self.express_img
        dlg.Destroy()


class CtrlPanel(wx.Panel):
    """ list panel  """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.start = Button(self, text=u"开始接驳", size=(120, 52), colour='green')
        self.pause = Button(self, u"暂停接驳", (120, 52), 'yellow')
        self.complete = Button(self, u"完成接驳", (120, 52), 'green')
        self.stop = Button(self, u"关机", (120, 52), 'red')
        self.login = Button(self, u"登录", (120, 52), 'white')

        sizer.Add(self.start, 0, wx.EXPAND)
        sizer.Add(self.pause, 0, wx.EXPAND | wx.LEFT, 50)
        sizer.Add(self.complete, 0, wx.EXPAND | wx.LEFT, 50)
        sizer.Add(self.stop, 0, wx.EXPAND | wx.LEFT, 50)
        sizer.Add(self.login, 0, wx.EXPAND | wx.LEFT, 50)

        self.Bind(wx.EVT_BUTTON, self.on_start, self.start)
        self.Bind(wx.EVT_BUTTON, self.on_pause, self.pause)
        self.Bind(wx.EVT_BUTTON, self.on_complete, self.complete)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop)
        self.Bind(wx.EVT_BUTTON, self.on_login, self.login)

        self.SetSizer(sizer)

    def on_login(self, _):
        """
        登录菜单
        """
        if server.uid is None:
            login = LoginDiolag(self)
            login.SetPosition((550, 250))
            login.ShowModal()
            if server.uid:
                self.login.SetLabel(u"注销")
            login.Destroy()
        else:
            server.logout()
            self.login.SetLabel(u"登录")

    def on_start(self, _):
        """
        设备启动菜单时间处理器
        点击启动菜单时调用该函数
        """
        if not server.selected:
            express_list = server.get_express_list()
            select = SelectDiolag(self, u"选择窗口", express_list)
            select.SetPosition((400, 200))
            select.ShowModal()
            if server.selected:
                watcher.publish(EVENT.SERIAL_CMD, "AA05start")
            else:
                server.clear_batch()
            select.Destroy()

    def on_pause(self, _):
        """ 暂停 """
        watcher.publish(EVENT.SERIAL_CMD, "AA04stop")

    def on_complete(self, _):
        """ 完成接驳 """
        server.clear_batch()
        watcher.publish(EVENT.SERIAL_CMD, "AA04stop")

    def on_stop(self, _):
        """ 关机 """
        watcher.publish(EVENT.SERIAL_CMD, "AA08shutdown")
