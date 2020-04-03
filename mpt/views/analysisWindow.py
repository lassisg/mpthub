# -*- coding: utf-8 -*-

###########################################################################
#
# Python code generated with wxFormBuilder (version Oct 26 2018)
# http://www.wxformbuilder.org/
#
###########################################################################

import wx
import wx.xrc


class analysisWindow (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, id=wx.ID_ANY,
                           title=u"Analysis configuration",
                           pos=wx.DefaultPosition, size=wx.Size(378, 235),
                           style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        main_diff_sizer = wx.BoxSizer(wx.VERTICAL)

        main_diff_sizer.Add((0, 0), 1, wx.EXPAND, 5)

        sz_config_1 = wx.BoxSizer(wx.HORIZONTAL)

        sz_config_1.Add((0, 0), 1, wx.EXPAND, 5)

        self.lbl_size = wx.StaticText(
            self, wx.ID_ANY, "Size (nm)",
            wx.DefaultPosition, wx.Size(70, -1), wx.ALIGN_RIGHT)
        self.lbl_size.Wrap(-1)

        sz_config_1.Add(
            self.lbl_size, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_size = wx.TextCtrl(
            self, id=wx.ID_ANY,
            value=f"{parent.analysis.config['p_size']}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER, name="p_size")
        sz_config_1.Add(self.txt_size, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sz_config_1.Add((0, 0), 1, wx.EXPAND, 5)

        self.lbl_filter = wx.StaticText(
            self, wx.ID_ANY, u"Filter",
            wx.DefaultPosition, wx.Size(70, -1), wx.ALIGN_RIGHT)
        self.lbl_filter.Wrap(-1)

        sz_config_1.Add(
            self.lbl_filter, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_filter = wx.TextCtrl(
            self, id=wx.ID_ANY,
            value=f"{parent.analysis.config['min_frames']}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER, name="min_frames")
        sz_config_1.Add(
            self.txt_filter, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sz_config_1.Add((0, 0), 1, wx.EXPAND, 5)

        main_diff_sizer.Add(sz_config_1, 1, wx.EXPAND, 5)

        sz_config_2 = wx.BoxSizer(wx.HORIZONTAL)

        sz_config_2.Add((0, 0), 1, wx.EXPAND, 5)

        self.lbl_fps = wx.StaticText(
            self, wx.ID_ANY, u"FPS",
            wx.DefaultPosition, wx.Size(70, -1), wx.ALIGN_RIGHT)
        self.lbl_fps.Wrap(-1)

        sz_config_2.Add(
            self.lbl_fps, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_fps = wx.TextCtrl(
            self, id=wx.ID_ANY,
            value=f"{parent.analysis.config['fps']}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER, name="fps")
        sz_config_2.Add(
            self.txt_fps, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sz_config_2.Add((0, 0), 1, wx.EXPAND, 5)

        self.lbl_frames = wx.StaticText(
            self, wx.ID_ANY, u"Frames",
            wx.DefaultPosition, wx.Size(70, -1), wx.ALIGN_RIGHT)
        self.lbl_frames.Wrap(-1)

        sz_config_2.Add(
            self.lbl_frames, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_frames = wx.TextCtrl(
            self, id=wx.ID_ANY,
            value=f"{parent.analysis.config['total_frames']}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER, name="total_frames")
        sz_config_2.Add(
            self.txt_frames, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sz_config_2.Add((0, 0), 1, wx.EXPAND, 5)

        main_diff_sizer.Add(sz_config_2, 1, wx.EXPAND, 5)

        sz_config_3 = wx.BoxSizer(wx.HORIZONTAL)

        sz_config_3.Add((0, 0), 1, wx.EXPAND, 5)

        self.lbl_width_px = wx.StaticText(
            self, wx.ID_ANY, u"Width (px)",
            wx.DefaultPosition, wx.Size(70, -1), wx.ALIGN_RIGHT)
        self.lbl_width_px.Wrap(-1)

        sz_config_3.Add(
            self.lbl_width_px, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_width_px = wx.TextCtrl(
            self, id=wx.ID_ANY,
            value=f"{parent.analysis.config['width_px']}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER, name="width_px")
        sz_config_3.Add(
            self.txt_width_px, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sz_config_3.Add((0, 0), 1, wx.EXPAND, 5)

        self.lbl_width_si = wx.StaticText(
            self, wx.ID_ANY, f"Width ({chr(956)}m)",
            wx.DefaultPosition, wx.Size(70, -1), wx.ALIGN_RIGHT)
        self.lbl_width_si.Wrap(-1)

        sz_config_3.Add(
            self.lbl_width_si, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_width_si = wx.TextCtrl(
            self, id=wx.ID_ANY,
            value=f"{parent.analysis.config['width_si']}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER, name="width_si")
        sz_config_3.Add(
            self.txt_width_si, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        sz_config_3.Add((0, 0), 1, wx.EXPAND, 5)

        main_diff_sizer.Add(sz_config_3, 1, wx.EXPAND, 5)

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
        # self.txt_size.Bind(wx.FOCUS, self.config_update)
        # self.txt_filter.Bind(wx.EVT_KILL_FOCUS, self.config_update)
        # self.txt_fps.Bind(wx.EVT_KILL_FOCUS, self.config_update)
        # self.txt_frames.Bind(wx.EVT_KILL_FOCUS, self.config_update)
        # self.txt_width_px.Bind(wx.EVT_KILL_FOCUS, self.config_update)
        # self.txt_width_si.Bind(wx.EVT_KILL_FOCUS, self.config_update)
        self.ctrl_buttonSave.Bind(wx.EVT_BUTTON, self.on_save_analysis)
        self.ctrl_buttonCancel.Bind(wx.EVT_BUTTON, self.on_cancel_analysis)

    # Virtual event handlers, overide them in your derived class

    def config_update(self):
        for widget in self.GetChildren():
            if widget.ClassName == 'wxTextCtrl':
                self.Parent.analysis.config[widget.Name] = widget.Value

    def on_save_analysis(self, event):
        self.Parent.statusBar.SetStatusText("Saving changes...")
        self.config_update()
        self.Parent.analysis.update(self.Parent.analysis.config)
        self.Destroy()

    def on_cancel_analysis(self, event):
        self.Parent.statusBar.SetStatusText("Canceling changes...")
        self.Destroy()
