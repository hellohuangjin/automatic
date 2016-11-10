#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" 自定义控件 """

import wx
import wx.grid
import wx.lib.buttons


class Text(wx.StaticText):
    """ 自定义静态文本显示 """

    def __init__(self, parent, text, size, style, font=20):
        font = wx.Font(font, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        super(Text, self).__init__(parent, wx.ID_ANY, text, size=size, style=style)
        self.SetFont(font)


class Button(wx.lib.buttons.GenButton):
    """自定义通用button"""

    def __init__(self, parent, text, size, colour, font=20):
        font = wx.Font(font, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        super(Button, self).__init__(parent, wx.ID_ANY, text, size=size)
        self.SetFont(font)
        self.SetBackgroundColour(colour)


class NoTitleGrid(wx.grid.Grid):
    """ 不带标题的表格 """

    def __init__(self, partner, row, col):
        super(NoTitleGrid, self).__init__(partner)
        self.SetColLabelSize(0)
        self.SetRowLabelSize(0)
        self.CreateGrid(row, col)
        self.SetDefaultCellAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)


class LabelTable(NoTitleGrid):
    """ 表格 """
    def __init__(self, partner):
        super(LabelTable, self).__init__(partner, 6, 2)
        self.SetColSize(0, 200)
        self.SetColSize(1, 250)
        font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetDefaultCellFont(font)
        self.SetDefaultRowSize(41)
        self.EnableEditing(False)

    def set_label(self, labels):
        """
        设置表格标题
        :param labels:标题列表
        :return None
        """
        for index, label in enumerate(labels):
            self.SetCellValue(index, 0, label)

    def set_data(self, data):
        """
        设置表格数据
        :param data:数据列表
        :return None
        """
        for index, value in enumerate(data):
            if isinstance(value, int):
                value = str(value)
            self.set_cell(index, value)

    def set_cell(self, row, value):
        """
        设置指定行单元格内容
        :param row: 行号
        :param value: 值
        :return: None
        """
        self.SetCellValue(row, 1, value)


class ListTable(NoTitleGrid):
    """ 列表 """
    def __init__(self, parent):
        super(ListTable, self).__init__(parent, 16, 3)
        self.SetColSize(0, 50)
        self.SetColSize(1, 250)
        self.SetColSize(2, 176)
        font = wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.SetDefaultCellFont(font)
        self.SetDefaultRowSize(50)
        self.EnableEditing(False)

    def set_label(self, labels):
        """
        设置列表的标题,传入标题列表
        :param labels:标题列表
        """
        for index, label in enumerate(labels):
            self.SetCellValue(0, index, label)

    def set_data(self, datas):
        """
        设置列表数据
        :param datas:数据列表
        return None
        """
        for index, data in enumerate(datas):
            self.set_cell(index+1, data)

    def set_cell(self, row, values):
        """
        设置列表制定行的值
        :param row:指定行
        :param values:需要设置的值，（id, num)
        """
        _id, bar, phone = values
        self.SetCellValue(row, 0, _id)
        self.SetCellValue(row, 1, bar)
        self.SetCellValue(row, 2, phone)
