# -*- coding: utf-8 -*-

###########################################################################
#
# Python code generated with wxFormBuilder (version Oct 26 2018)
# http://www.wxformbuilder.org/
#
###########################################################################

import wx
import wx.xrc
import wx.dataview
import mpt
from . import analysisWindow, diffusivityWindow
from mpt.settings import Settings
import os


class mainWindow (wx.Frame):

    def __init__(self, parent) -> None:
        wx.Frame.__init__(self, parent, id=wx.ID_ANY,
                          title=u"Multiple Particle Tracking",
                          pos=wx.DefaultPosition, size=wx.Size(688, 480),
                          style=wx.SYSTEM_MENU | wx.CAPTION |
                          wx.MINIMIZE_BOX | wx.CLOSE_BOX)

        settings = Settings()
        self.SetIcon(wx.Icon(os.path.join(settings.ICON_PATH, "icon.ico")))
        self.SetSizeHints(wx.Size(688, 480), wx.Size(688, 480))
        self.create_menu_bar()
        self.create_layout()
        self.create_status_bar()
        self.load_project_setup()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Centre(wx.BOTH)

    def create_menu_bar(self) -> None:
        menu_bar = wx.MenuBar()
        for data in self.menu_data():
            menu_label = data[0]
            menu_items = data[1]
            menu_bar.Append(self.create_menu(menu_items), menu_label)
            self.SetMenuBar(menu_bar)

    def create_menu(self, menu_data) -> wx.Menu:
        menu = wx.Menu()
        for item in menu_data:
            if len(item) == 2:
                label = item[0]
                sub_menu = self.create_menu(item[1])
                menu.AppendMenu(wx.NewId(), label, sub_menu)
            else:
                self.create_menu_item(menu, *item)
        return menu

    def create_menu_item(self, menu, label, status, handler, is_enabled,
                         kind=wx.ITEM_NORMAL) -> None:

        if not label:
            menu.AppendSeparator()
            return
        menu_item = menu.Append(-1, label, status, kind)
        self.Bind(wx.EVT_MENU, handler, menu_item)
        menu_item.Enable(is_enabled)

    def menu_data(self) -> list:
        # TODO: Get from db or settings file
        return [("&File", (("&Open files",
                            "Open ImageJ result file(s)",
                            self.on_mnuImport, True),
                           ("&Save reports",
                            "Save analysis report files",
                            self.on_mnuExport, False))),
                ("&Tools", (("App configuration",
                             "General configuration",
                             self.on_mnuGeneral, True),
                            ("Diffusivity configuration",
                             "Diffusivity ranges configuration",
                             self.on_mnuDiffusivity, True),
                            ("", "", "", True),
                            ("Start analysis",
                             "Starts MPT analysis",
                             self.on_mnuAnalysis, False))),
                ("&Help", (("&Documentation",
                            "Application documentation",
                            self.on_mnuHelp, False),
                           ("&About",
                            "About this program",
                            self.on_mnuAbout, False)))]

    def create_layout(self) -> None:
        mainBoxSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.dataListView = wx.dataview.DataViewListCtrl(
            self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize,
            wx.dataview.DV_HORIZ_RULES | wx.dataview.DV_ROW_LINES |
            wx.dataview.DV_VARIABLE_LINE_HEIGHT | wx.BORDER_NONE)
        self.col_name = self.dataListView.AppendTextColumn(
            "File name", wx.dataview.DATAVIEW_CELL_INERT, 466,
            wx.ALIGN_LEFT, 0)
        self.col_trajectories = self.dataListView.AppendTextColumn(
            "Total trajectories", wx.dataview.DATAVIEW_CELL_INERT, 102,
            wx.ALIGN_RIGHT, 0)
        self.col_trajectories = self.dataListView.AppendTextColumn(
            "Valid trajectories", wx.dataview.DATAVIEW_CELL_INERT, 102,
            wx.ALIGN_RIGHT, 0)

        mainBoxSizer.Add(self.dataListView, 1, wx.EXPAND, 1)

        self.SetSizer(mainBoxSizer)
        self.Layout()

    def create_status_bar(self) -> None:
        self.statusBar = self.CreateStatusBar(1, wx.STB_SIZEGRIP, wx.ID_ANY)

    def load_project_setup(self) -> None:
        self.analysis = mpt.analysis
        self.diffusivity = mpt.diffusivity
        self.general = mpt.general

    def on_mnuImport(self, event) -> None:
        self.get_summary()
        self.update_list_view()
        # TODO: Find a way to avoid using text as parameters
        self.toggle_menu_item(
            self.MenuBar.FindMenuItem("Tools", "Start analysis"),
            not self.analysis.summary.empty)

    def get_summary(self) -> None:
        with wx.FileDialog(None, "Open ImageJ Full report file(s)",
                           wildcard="ImageJ full report files (*.csv)|*.csv",
                           style=wx.FD_OPEN | wx.FD_MULTIPLE) as fileDialog:

            fileDialog.SetDirectory(self.general.config.open_folder)
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                self.statusBar.SetStatusText("No file selected...")
                return None

            self.statusBar.SetStatusText("File(s) selected...")
            file_list = fileDialog.GetPaths()
            self.analysis.load_reports(self, file_list)

            self.general.config.open_folder = fileDialog.GetDirectory()
            self.general.update(self.general.config)
            self.statusBar.SetStatusText("Data fetched!")

    def update_list_view(self) -> None:
        total_trajectories = 0
        total_valid_trajectories = 0

        self.dataListView.DeleteAllItems()
        for index, report in self.analysis.summary.iterrows():
            total_trajectories += report.trajectories
            total_valid_trajectories += report.valid
            self.dataListView.AppendItem([report.full_path,
                                          report.trajectories,
                                          report.valid])

        self.dataListView.AppendItem(["Total",
                                      total_trajectories,
                                      total_valid_trajectories])

    def toggle_menu_item(self, menu_item_id: int, enable: bool) -> None:
        self.MenuBar.FindItem(menu_item_id)[0].Enable(enable)

    def on_mnuAnalysis(self, event):
        self.statusBar.SetStatusText("Starts analysis...")
        self.analysis.start(self)
        self.toggle_menu_item(
            self.MenuBar.FindMenuItem("File", "Save reports"),
            not self.analysis.msd.empty)
        self.statusBar.SetStatusText("Analysis complete...")

    def on_mnuExport(self, event):
        self.statusBar.SetStatusText("Open dialog to set export folder...")

        with wx.DirDialog(
                None, message=f"Chose folder to save report files",
                defaultPath=self.general.config.save_folder) as saveDialog:

            # TODO: Add save path to app_config table
            if saveDialog.ShowModal() == wx.ID_CANCEL:
                self.statusBar.SetStatusText("Canceling report saving...")

            self.general.config.save_folder = saveDialog.GetPath()
            self.general.update(self.general.config)
            self.statusBar.SetStatusText(
                f"Saving reports to {self.general.config.save_folder}...")
            self.analysis.export(self)

    def on_mnuDiffusivity(self, event) -> None:
        self.statusBar.SetStatusText("Open dialog for diffusivity setup...")
        diffusivityWindow(self).ShowModal()

    def on_mnuGeneral(self, event) -> None:
        self.statusBar.SetStatusText("Open dialog for general setup...")
        analysisWindow(self).ShowModal()

    def on_mnuHelp(self, event):
        self.statusBar.SetStatusText("Open Help window...")

    def on_mnuAbout(self, event):
        self.statusBar.SetStatusText("Open About window...")

    def on_close(self, event) -> None:
        self.analysis.clear_trajectories()
        self.Destroy()
