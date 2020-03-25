# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version Oct 26 2018)
# http://www.wxformbuilder.org/
##
# PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
from mpt.model import Diffusivity

###########################################################################
# Class diffusivityWindow
###########################################################################


class diffusivityWindow (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(
            self, parent, id=wx.ID_ANY,
            title=u"Transport mode diffusivity ranges configuration",
            pos=wx.DefaultPosition, size=wx.Size(353, 255),
            style=wx.DEFAULT_DIALOG_STYLE)

        self.model = Diffusivity()
        self.config = self.model.load_config()

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        main_diff_sizer = wx.BoxSizer(wx.VERTICAL)

        main_diff_sizer.Add((0, 0), 1, wx.EXPAND, 5)

        sz_immobile = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl_immobile = wx.StaticText(
            self, wx.ID_ANY, u"Immobile", wx.DefaultPosition,
            wx.DefaultSize, wx.ALIGN_RIGHT)
        self.lbl_immobile.Wrap(-1)

        sz_immobile.Add(
            self.lbl_immobile, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_immobile_min = wx.TextCtrl(
            self, wx.ID_ANY, f"{self.config['immobile']['min']}",
            wx.DefaultPosition, wx.Size(43, -1),
            wx.TE_CENTER | wx.TE_READONLY)
        sz_immobile.Add(
            self.txt_immobile_min, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.lbl_immobile_sep = wx.StaticText(
            self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lbl_immobile_sep.Wrap(-1)

        sz_immobile.Add(
            self.lbl_immobile_sep, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_immobile_max = wx.TextCtrl(
            self, wx.ID_ANY, f"{self.config['immobile']['max']}",
            wx.DefaultPosition, wx.Size(43, -1),
            wx.TE_CENTER | wx.TE_READONLY)
        sz_immobile.Add(
            self.txt_immobile_max, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sz_immobile.Add((0, 0), 1, wx.EXPAND, 5)

        main_diff_sizer.Add(sz_immobile, 1, wx.EXPAND, 5)

        sz_subdiffusive = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl_subdiffusive = wx.StaticText(
            self, wx.ID_ANY, u"Sub-diffusive",
            wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT)
        self.lbl_subdiffusive.Wrap(-1)

        sz_subdiffusive.Add(
            self.lbl_subdiffusive, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_subdiffusive_min = wx.TextCtrl(
            self, wx.ID_ANY, f"{self.config['sub_diffusive']['min']}",
            wx.DefaultPosition, wx.Size(43, -1), wx.TE_CENTER)
        sz_subdiffusive.Add(
            self.txt_subdiffusive_min, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.lbl_subdiffusive_sep = wx.StaticText(
            self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lbl_subdiffusive_sep.Wrap(-1)

        sz_subdiffusive.Add(
            self.lbl_subdiffusive_sep, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_subdiffusive_max = wx.TextCtrl(
            self, wx.ID_ANY, f"{self.config['sub_diffusive']['max']}",
            wx.DefaultPosition, wx.Size(43, -1),
            wx.TE_CENTER | wx.TE_READONLY)
        sz_subdiffusive.Add(
            self.txt_subdiffusive_max, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sz_subdiffusive.Add((0, 0), 1, wx.EXPAND, 5)

        main_diff_sizer.Add(sz_subdiffusive, 1, wx.EXPAND, 5)

        sz_diffusive = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl_diffusive = wx.StaticText(
            self, wx.ID_ANY, u"Diffusive",
            wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT)
        self.lbl_diffusive.Wrap(-1)

        sz_diffusive.Add(
            self.lbl_diffusive, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_diffusive_min = wx.TextCtrl(
            self, wx.ID_ANY, f"{self.config['diffusive']['min']}",
            wx.DefaultPosition, wx.Size(43, -1), wx.TE_CENTER)
        sz_diffusive.Add(
            self.txt_diffusive_min, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.lbl_diffusive_sep = wx.StaticText(
            self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lbl_diffusive_sep.Wrap(-1)

        sz_diffusive.Add(
            self.lbl_diffusive_sep, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_diffusive_max = wx.TextCtrl(
            self, wx.ID_ANY, f"{self.config['diffusive']['max']}",
            wx.DefaultPosition, wx.Size(43, -1),
            wx.TE_CENTER | wx.TE_READONLY)
        sz_diffusive.Add(
            self.txt_diffusive_max, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sz_diffusive.Add((0, 0), 1, wx.EXPAND, 5)

        main_diff_sizer.Add(sz_diffusive, 1, wx.EXPAND, 5)

        sz_active = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl_active = wx.StaticText(
            self, wx.ID_ANY, u"Active",
            wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT)
        self.lbl_active.Wrap(-1)

        sz_active.Add(self.lbl_active, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_active_min = wx.TextCtrl(
            self, wx.ID_ANY, f"{self.config['active']['min']}",
            wx.DefaultPosition, wx.Size(43, -1), wx.TE_CENTER)
        sz_active.Add(
            self.txt_active_min, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.lbl_active_sep = wx.StaticText(
            self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lbl_active_sep.Wrap(-1)

        sz_active.Add(
            self.lbl_active_sep, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_active_max = wx.TextCtrl(
            self, wx.ID_ANY, f"{self.config['active']['min']}+",
            wx.DefaultPosition, wx.Size(43, -1), wx.TE_CENTER | wx.TE_READONLY)
        sz_active.Add(
            self.txt_active_max, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sz_active.Add((0, 0), 1, wx.EXPAND, 5)

        main_diff_sizer.Add(sz_active, 1, wx.EXPAND, 5)

        main_diff_sizer.Add((0, 0), 1, wx.EXPAND, 5)

        ctrl_button = wx.StdDialogButtonSizer()
        self.ctrl_buttonSave = wx.Button(self, wx.ID_SAVE)
        ctrl_button.AddButton(self.ctrl_buttonSave)
        self.ctrl_buttonCancel = wx.Button(self, wx.ID_CANCEL)
        ctrl_button.AddButton(self.ctrl_buttonCancel)
        ctrl_button.Realize()

        main_diff_sizer.Add(ctrl_button, 1, wx.EXPAND, 5)

        self.SetSizer(main_diff_sizer)
        self.Layout()

        self.Centre(wx.BOTH)

        # Connect Events
        self.txt_subdiffusive_min.Bind(
            wx.EVT_TEXT, self.on_subdiffusive_range_change)
        self.txt_diffusive_min.Bind(
            wx.EVT_TEXT, self.on_diffusive_range_change)
        self.txt_active_min.Bind(
            wx.EVT_TEXT, self.on_active_range_change)
        self.ctrl_buttonSave.Bind(
            wx.EVT_BUTTON, self.on_save_diffusivity)
        self.ctrl_buttonCancel.Bind(
            wx.EVT_BUTTON, self.on_cancel_diffusivity)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def on_subdiffusive_range_change(self, event):
        self.config['sub_diffusive']['min'] = float(
            self.txt_subdiffusive_min.Value)

        self.config['immobile']['max'] = float(
            self.txt_subdiffusive_min.Value)-.001

        self.txt_immobile_max.SetValue(
            f"{self.config['immobile']['max']}")

        event.Skip()

    def on_diffusive_range_change(self, event):
        self.config['diffusive']['min'] = float(
            self.txt_diffusive_min.Value)

        self.config['sub_diffusive']['max'] = float(
            self.txt_diffusive_min.Value)-.001

        self.txt_subdiffusive_max.SetValue(
            f"{self.config['sub_diffusive']['max']}")

        event.Skip()

    def on_active_range_change(self, event):
        self.config['active']['min'] = float(
            self.txt_active_min.Value)

        self.config['diffusive']['max'] = float(
            self.txt_active_min.Value)-.001

        self.txt_diffusive_max.SetValue(
            f"{self.config['diffusive']['max']}")

        self.txt_active_max.SetValue(
            f"{self.config['active']['min']}+")

        event.Skip()

    def on_save_diffusivity(self, event):
        self.model.update(self.config)
        self.Destroy()
        event.Skip()

    def on_cancel_diffusivity(self, event):
        print("Aborting changes...")
        self.Destroy()
        event.Skip()
