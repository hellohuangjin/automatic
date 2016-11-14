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
        self.frame.Close()
        error = ErrorFrame(parent=None, msg=msg)
        error.show()

    def show(self):
        """显示界面"""
        self.frame.ShowFullScreen(True)
        self.app.MainLoop()


class ErrorFrame(object):
    """错误信息界面"""

    def __init__(self, parent, msg=None):
        self.dlg = wx.MessageDialog(parent, msg, u"程序错误", wx.OK | wx.ICON_ERROR)

    def show(self):
        self.dlg.ShowModal()
        exit(0)

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

        self.SetBackgroundColour((207, 207, 207))

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
        self.SetBackgroundColour((207, 207, 207))
        self.table = ListTable(self)
        self.table.SetSize((476, 700))
        self.table.set_label(["id", u"运单号", u"手机号"])
        self.index = 0
        self.data = list()
        watcher.attach(EVENT.REG_PHONE, self.new_data)
        watcher.attach(EVENT.EVT_COMPLETE, self.clear)

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
        watcher.attach(EVENT.EVT_START, self.change_status)
        watcher.attach(EVENT.EVT_PAUSE, self.change_status)
        watcher.attach(EVENT.EVT_URGENCY, self.change_status)
        watcher.attach(EVENT.EVT_COMPLETE, self.change_status)
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

        labels = [u"快递公司", u"接驳批次", u"快件总数", u"接驳数", u"手机号识别数", u"异常件数"]

        self.table = LabelTable(self)
        self.table.SetSize((450, 246))
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
        self.SetBackgroundColour((207, 207, 207))
        self.urgency = False
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

        watcher.attach(EVENT.EVT_URGENCY, self.urgency_event)
        watcher.attach(EVENT.CLEAR, self.urgency_event)

        self.SetSizer(sizer)

    def urgency_event(self, msg):
        if msg == 'urgency':
            self.urgency = True
        elif msg == 'clear':
            self.urgency = False

    def on_login(self, _):
        """
        登录菜单
        """
        if self.urgency:
            return
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
        if self.urgency:
            return
        all_key_in = "batch_id" in server.selected and "express_id" in server.selected
        if not all_key_in:
            express_list = server.get_express_list()
            select = SelectDiolag(self, u"选择窗口", express_list)
            select.SetPosition((400, 200))
            select.ShowModal()
            all_key_in = "batch_id" in server.selected and "express_id" in server.selected
            if all_key_in:
                watcher.info[0], watcher.info[1] = select.get_select_info()
                watcher.publish(EVENT.SERIAL_CMD, "AA05start")
                watcher.publish(EVENT.EVT_START, "start")
                watcher.publish(EVENT.EVT_UPDATE, None)
            else:
                server.clear_batch()
            select.Destroy()
        else:
            watcher.publish(EVENT.SERIAL_CMD, "AA05start")
            watcher.publish(EVENT.EVT_START, "start")

    def on_pause(self, _):
        """ 暂停 """
        if self.urgency:
            return
        watcher.publish(EVENT.SERIAL_CMD, "AA04stop")
        watcher.publish(EVENT.EVT_PAUSE, 'pause')

    def on_complete(self, _):
        """ 完成接驳 """
        if self.urgency:
            return
        server.clear_batch()
        watcher.publish(EVENT.EVT_COMPLETE, 'complete')
        watcher.publish(EVENT.SERIAL_CMD, "AA04stop")
        watcher.info[0] = u"尚未接驳"
        watcher.info[1] = u"尚未接驳"
        watcher.info[2] = 0;
        watcher.info[3] = 0;
        watcher.info[4] = 0;
        watcher.info[5] = 0;
        watcher.publish(EVENT.EVT_UPDATE, None)

    def on_stop(self, _):
        """ 关机 """
        watcher.publish(EVENT.SERIAL_CMD, "AA08shutdown")
        exit(0)
