# -*- coding: utf-8 -*-

###########################################################################
# Python code generated with wxFormBuilder (version Oct 26 2018)
# http://www.wxformbuilder.org/
##
# PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.dataview
from .diffusivityWindow import diffusivityWindow
###########################################################################
# Class mainWindow
###########################################################################


class mainWindow (wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY,
                          title=u"Multiple Particle Tracking",
                          pos=wx.DefaultPosition, size=wx.Size(688, 480),
                          style=wx.SYSTEM_MENU | wx.CAPTION |
                          wx.MINIMIZE_BOX | wx.CLOSE_BOX)

        # self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        self.SetSizeHints(wx.Size(688, 480), wx.Size(688, 480))

        self.mnuBar = wx.MenuBar(0)
        self.mnuFile = wx.Menu()
        self.mnuImport = wx.MenuItem(self.mnuFile, wx.ID_ANY,
                                     u"Import files",
                                     wx.EmptyString, wx.ITEM_NORMAL)
        self.mnuFile.Append(self.mnuImport)

        self.mnuExport = wx.MenuItem(self.mnuFile, wx.ID_ANY,
                                     u"Export reports",
                                     wx.EmptyString, wx.ITEM_NORMAL)
        self.mnuFile.Append(self.mnuExport)

        self.mnuBar.Append(self.mnuFile, u"File")

        self.mnuTools = wx.Menu()
        self.mnuAnalysis = wx.MenuItem(self.mnuTools, wx.ID_ANY,
                                       u"Start analysis",
                                       wx.EmptyString, wx.ITEM_NORMAL)
        self.mnuTools.Append(self.mnuAnalysis)

        self.mnuConfig = wx.Menu()
        self.mnuDiffusivity = wx.MenuItem(self.mnuConfig, wx.ID_ANY,
                                          u"Diffisivity ranges",
                                          wx.EmptyString, wx.ITEM_NORMAL)
        self.mnuConfig.Append(self.mnuDiffusivity)

        self.mnuGeneral = wx.MenuItem(self.mnuConfig, wx.ID_ANY,
                                      u"Analysis configuration",
                                      wx.EmptyString, wx.ITEM_NORMAL)
        self.mnuConfig.Append(self.mnuGeneral)

        self.mnuTools.AppendSubMenu(self.mnuConfig, u"Configurations")

        self.mnuBar.Append(self.mnuTools, u"Tools")

        self.mnuHelp = wx.Menu()
        self.mnuBar.Append(self.mnuHelp, u"Help")

        self.SetMenuBar(self.mnuBar)

        mainBoxSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.dataListView = wx.dataview.DataViewListCtrl(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.dataview.DV_HORIZ_RULES | wx.dataview.DV_ROW_LINES |
            wx.dataview.DV_VARIABLE_LINE_HEIGHT | wx.BORDER_NONE)
        self.col_name = self.dataListView.AppendTextColumn(
            u"File name", wx.dataview.DATAVIEW_CELL_INERT, 520,
            wx.ALIGN_LEFT, 0)
        self.col_trajectories = self.dataListView.AppendTextColumn(
            u"Valid trajectories", wx.dataview.DATAVIEW_CELL_INERT, 120,
            wx.ALIGN_RIGHT, 0)

        mainBoxSizer.Add(self.dataListView, 1, wx.EXPAND, 1)

        self.SetSizer(mainBoxSizer)
        self.Layout()
        self.statusBar = self.CreateStatusBar(1, wx.STB_SIZEGRIP, wx.ID_ANY)

        self.Centre(wx.BOTH)

        # Connect Events
        self.Bind(wx.EVT_MENU, self.on_mnuImport,
                  id=self.mnuImport.GetId())
        self.Bind(wx.EVT_MENU, self.on_mnuExport,
                  id=self.mnuExport.GetId())
        self.Bind(wx.EVT_MENU, self.on_mnuAnalysis,
                  id=self.mnuAnalysis.GetId())
        self.Bind(wx.EVT_MENU, self.on_mnuDiffusivity,
                  id=self.mnuDiffusivity.GetId())
        self.Bind(wx.EVT_MENU, self.on_mnuGeneral,
                  id=self.mnuGeneral.GetId())

    # Virtual event handlers, overide them in your derived class

    def on_mnuImport(self, event):
        self.statusBar.SetStatusText("Open file dialog to import files...")
        event.Skip()

    def on_mnuExport(self, event):
        self.statusBar.SetStatusText("Open dialog to set export folder...")
        event.Skip()

    def on_mnuAnalysis(self, event):
        self.statusBar.SetStatusText("Starts analysis...")
        event.Skip()

    def on_mnuDiffusivity(self, event):
        self.statusBar.SetStatusText("Open dialog for diffusivity setup...")
        # dialog = diffusivityWindow.diffusivityWindow()
        # dlg = wx.Dialog()
        a = diffusivityWindow(self).ShowModal()
        event.Skip()

    def on_mnuGeneral(self, event):
        self.statusBar.SetStatusText("Open dialog for general setup...")
        event.Skip()

    def __del__(self):
        pass
