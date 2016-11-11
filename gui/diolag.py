#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wx
from context import server
from gui.custome import Text, Button


class LoginDiolag(wx.Dialog):
    """登录对话框"""

    def __init__(self, parent):
        super(LoginDiolag, self).__init__(parent, title=u"登录", size=(350, 260))
        panel = wx.Panel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)

        name_sizer = wx.BoxSizer(wx.HORIZONTAL)
        pass_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)

        name_label = Text(panel, u"用户名", size=(75, 30), style=wx.TE_CENTER, font=18)
        self.name = wx.TextCtrl(panel, wx.ID_ANY, size=(200, 30), style=wx.TE_CENTER)
        self.name.SetFont(font)
        name_sizer.Add(name_label, 0, wx.EXPAND | wx.TOP | wx.LEFT, 25)
        name_sizer.Add(self.name, 0, wx.EXPAND | wx.TOP | wx.LEFT, 25)

        password_label = Text(panel, u"密  码", size=(75, 30), style=wx.TE_CENTER, font=18)
        self.password = wx.TextCtrl(panel, wx.ID_ANY, size=(200, 30), style=wx.TE_PASSWORD|wx.TE_CENTER)
        self.password.SetFont(font)
        pass_sizer.Add(password_label, 0, wx.TOP | wx.LEFT, 25)
        pass_sizer.Add(self.password, 0, wx.RIGHT | wx.TOP | wx.LEFT, 25)

        button_clean = Button(panel, u"清除", (100, 50), 'red')
        button_login = Button(panel, u"登录", (100, 50), 'green')
        btn_sizer.Add(button_clean, 0, wx.LEFT | wx.TOP, 50)
        btn_sizer.Add(button_login, 0, wx.LEFT | wx.TOP | wx.RIGHT, 50)

        sizer.AddMany([name_sizer, pass_sizer, btn_sizer])
        panel.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.clean, button_clean)
        self.Bind(wx.EVT_BUTTON, self.login, button_login)

    def clean(self, _):
        """清除"""
        self.name.Clear()
        self.password.Clear()

    def login(self, _):
        name = self.name.GetValue()
        password = self.password.GetValue()
        if name != "" and password != "":
            logis_list = server.login(name, password)
            if len(logis_list) > 1:
                index = self.select_logis([item['name'] for item in logis_list])
                if index is not None:
                    server.logis = logis_list[index]
                else:
                    server.logout()
            else:
                server.logis = logis_list[0]
            self.Close()

    def select_logis(self, logis_names):
        dlg = wx.SingleChoiceDialog(self, u"选择一个物流中心", u"物流中心", logis_names)
        code = dlg.ShowModal()

        if code == wx.ID_OK:
            return dlg.GetSelection()
        return None


class SelectDiolag(wx.Dialog):
    """ 快递公司、批次选择对话狂 """

    def __init__(self, parent, title, express_list):
        """
        初始化
        :param parent:父元素
        :param title:标题
        :param express_list:快递公司列表
        """
        super(SelectDiolag, self).__init__(parent, title=title, size=(400, 400))
        font = wx.Font(15, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        panel = wx.Panel(self)
        comb_label = Text(panel, u"选择合作方", size=(150, 40), style=wx.TE_LEFT, font=15)
        self.express_list = express_list
        express_name = [item['name'] for item in express_list]
        self.company = wx.ComboBox(panel, choices=express_name, style=wx.CB_DROPDOWN)
        self.company.SetFont(font)
        batch_label = Text(panel, text=u"请选择批次", size=(150, 40), style=wx.TE_LEFT, font=15)
        self.batch = wx.ComboBox(panel, choices=[], style=wx.CB_DROPDOWN)
        self.batch.SetFont(font)

        self.company.Bind(wx.EVT_COMBOBOX, self.get_batch_list)

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(comb_label, 0, wx.TOP | wx.LEFT | wx.BOTTOM, 30)
        sizer.Add(self.company, 0, wx.EXPAND | wx.LEFT | wx.BOTTOM | wx.RIGHT, 30)
        sizer.Add(batch_label, 0, wx.LEFT | wx.BOTTOM, 30)
        sizer.Add(self.batch, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 30)

        bottom = wx.BoxSizer(wx.HORIZONTAL)

        new_button = Button(panel, u"新建批次", (100, 80), "white", font=18)
        new_button.Bind(wx.EVT_BUTTON, self.add_batch)
        conform_button = Button(panel, u"开始接驳", (100, 80), 'white', font=18)
        conform_button.Bind(wx.EVT_BUTTON, self.start_accept)
        bottom.Add(new_button, 0)
        bottom.Add(conform_button, 0, wx.LEFT, 60)

        sizer.Add(bottom, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 50)

        panel.SetSizer(sizer)

    def start_accept(self, _):
        company = self.company.GetSelection()
        batch = self.batch.GetSelection()
        if company != -1 and batch != -1:
            self.Close()

    def get_batch_list(self, _):
        index = self.company.GetSelection()
        if index != -1:
            self.batch_list = server.get_batch_list(self.express_list[index]['id'])
            for batch in self.batch_list:
                self.batch.Append(batch['batch_date']+str(batch['seq_no']))

    def select_batch(self, _):
        index = self.batch.GetSelection()
        batch_id = self.batch_list[index-1]['id']
        server.selected['batch_id'] = batch_id

    def add_batch(self, _):
        body = server.batch_pre_add()
        if body:
            dlg = wx.MessageDialog(self,
                                   body['batch_date']+":"+u'第'+str(body['next_seq_no'])+u'批',
                                   u"确认创建",
                                   style=wx.YES_NO | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                body = server.batch_add(body['batch_date'], body['next_seq_no'])
                batch = body[0]
                server.selected['batch_id'] = batch['id']
                self.batch.Append(batch['batch_date'] + str(batch['seq_no']))


class ImageExplore(wx.Dialog):
    """
    原始面单图片浏览窗口
    """
    def __init__(self, parent, title):
        super(ImageExplore, self).__init__(parent, title=title)
        panel = wx.Panel(self)
        self.img = wx.StaticBitmap(panel, -1, wx.NullBitmap)

    def SetBitmap(self, bitmap):
        """
        更改显示图片，bitmap为wx框架图片
        :param bitmap:显示图片
        :return None
        """
        self.img.SetBitmap(bitmap)
