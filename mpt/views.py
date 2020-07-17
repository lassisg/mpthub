
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
from .settings import Settings
import os
import time


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
                ("&Edit", (("App configuration",
                            "General configuration",
                            self.on_mnuGeneral, True),
                           ("Diffusivity configuration",
                            "Diffusivity ranges configuration",
                            self.on_mnuDiffusivity, True),
                           ("", "", "", True),
                           ("Start analysis",
                            "Starts MPT analysis",
                            self.on_mnuAnalysis, False),
                           ("", "", "", True),
                           ("Clear summary",
                            "Clear current summary list",
                            self.on_mnuClear, False),
                           ("Remove selected",
                            "Remove selected files from summary list",
                            self.on_mnuRemove, False))),
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
        self.col_remove = self.dataListView.AppendToggleColumn(
            "Remove", wx.dataview.DATAVIEW_CELL_ACTIVATABLE, 21,
            wx.ALIGN_CENTER, 0)
        self.col_name = self.dataListView.AppendTextColumn(
            "File name", wx.dataview.DATAVIEW_CELL_INERT, 444,
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
            self.MenuBar.FindMenuItem("Edit", "Start analysis"),
            not self.analysis.summary.empty)
        self.toggle_menu_item(
            self.MenuBar.FindMenuItem("Edit", "Clear summary"),
            not self.analysis.summary.empty)
        self.toggle_menu_item(
            self.MenuBar.FindMenuItem("Edit", "Remove selected"),
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
            self.dataListView.AppendItem([False,
                                          report.full_path,
                                          str(int(report.trajectories)),
                                          str(int(report.valid))])

        self.dataListView.AppendItem([False,
                                      "Total",
                                      str(int(total_trajectories)),
                                      str(int(total_valid_trajectories))])

    def toggle_menu_item(self, menu_item_id: int, enable: bool) -> None:
        self.MenuBar.FindItem(menu_item_id)[0].Enable(enable)

    def on_mnuAnalysis(self, event):
        self.statusBar.SetStatusText(
            f"Starting multiple particle analysis...")

        start = time.time()
        print(f"Start time: {start}")
        self.analysis.start(self)
        end = time.time()
        print(f"End time: {end}")
        print(f"Elapsed time: {end - start}")

        self.toggle_menu_item(
            self.MenuBar.FindMenuItem("File", "Save reports"),
            not self.analysis.msd.empty)
        self.statusBar.SetStatusText("Analysis complete...")

    def on_mnuExport(self, event):

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

            self.statusBar.SetStatusText("Reports saved.")

    def on_mnuRemove(self, event):

        row = 0
        while row < self.dataListView.ItemCount - 1:
            if self.dataListView.GetToggleValue(row, 0):
                self.dataListView.DeleteItem(row)
                row -= 1

            row += 1

        if self.dataListView.ItemCount == 1:
            self.clear_summary()

    def on_mnuClear(self, event):
        self.statusBar.SetStatusText(f"Starting summary clear...")
        self.clear_summary()
        self.analysis.clear_summary()
        self.toggle_menu_item(
            self.MenuBar.FindMenuItem("Edit", "Start analysis"),
            not self.analysis.summary.empty)
        self.toggle_menu_item(
            self.MenuBar.FindMenuItem("Edit", "Clear summary"),
            not self.analysis.summary.empty)

    def clear_summary(self):
        self.dataListView.DeleteAllItems()

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


class diffusivityWindow (wx.Dialog):

    def __init__(self, parent):
        wx.Dialog.__init__(
            self, parent, id=wx.ID_ANY,
            title=u"Transport mode diffusivity ranges configuration",
            pos=wx.DefaultPosition, size=wx.Size(353, 255),
            style=wx.DEFAULT_DIALOG_STYLE)

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
            self, wx.ID_ANY, f"{parent.diffusivity.config.immobile[0]}",
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
            self, wx.ID_ANY, f"{parent.diffusivity.config.immobile[1]}",
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
            self, id=wx.ID_ANY,
            value=f"{parent.diffusivity.config.sub_diffusive[0]}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER, name="sub_diffusive-min")
        sz_subdiffusive.Add(
            self.txt_subdiffusive_min, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.lbl_subdiffusive_sep = wx.StaticText(
            self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lbl_subdiffusive_sep.Wrap(-1)

        sz_subdiffusive.Add(
            self.lbl_subdiffusive_sep, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_subdiffusive_max = wx.TextCtrl(
            self, id=wx.ID_ANY,
            value=f"{parent.diffusivity.config.sub_diffusive[1]}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER | wx.TE_READONLY, name="sub_diffusive-max")
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
            self, id=wx.ID_ANY,
            value=f"{parent.diffusivity.config.diffusive[0]}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER, name="diffusive-min")
        sz_diffusive.Add(
            self.txt_diffusive_min, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.lbl_diffusive_sep = wx.StaticText(
            self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lbl_diffusive_sep.Wrap(-1)

        sz_diffusive.Add(
            self.lbl_diffusive_sep, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_diffusive_max = wx.TextCtrl(
            self, id=wx.ID_ANY,
            value=f"{parent.diffusivity.config.diffusive[1]}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER | wx.TE_READONLY, name="diffusive-max")
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
            self, id=wx.ID_ANY,
            value=f"{parent.diffusivity.config.active[0]}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER, name="active-min")
        sz_active.Add(
            self.txt_active_min, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.lbl_active_sep = wx.StaticText(
            self, wx.ID_ANY, u"-", wx.DefaultPosition, wx.DefaultSize, 0)
        self.lbl_active_sep.Wrap(-1)

        sz_active.Add(
            self.lbl_active_sep, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)

        self.txt_active_max = wx.TextCtrl(
            self, id=wx.ID_ANY,
            value=f"{chr(8734)}",
            pos=wx.DefaultPosition, size=wx.Size(43, -1),
            style=wx.TE_CENTER | wx.TE_READONLY, name="active-max")
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
            wx.EVT_KILL_FOCUS, self.on_subdiffusive_range_change)
        self.txt_diffusive_min.Bind(
            wx.EVT_KILL_FOCUS, self.on_diffusive_range_change)
        self.txt_active_min.Bind(
            wx.EVT_KILL_FOCUS, self.on_active_range_change)
        self.ctrl_buttonSave.Bind(
            wx.EVT_BUTTON, self.on_save_diffusivity)
        self.ctrl_buttonCancel.Bind(
            wx.EVT_BUTTON, self.on_cancel_diffusivity)

    def __del__(self):
        pass

    # Virtual event handlers, overide them in your derived class
    def on_subdiffusive_range_change(self, event):
        self.Parent.diffusivity.config.sub_diffusive[0] = float(
            self.txt_subdiffusive_min.Value)

        self.Parent.diffusivity.config.immobile[1] = float(
            self.txt_subdiffusive_min.Value)-.001

        self.txt_immobile_max.SetValue(
            f"{self.Parent.diffusivity.config.immobile[1]}")

    def on_diffusive_range_change(self, event):
        self.Parent.diffusivity.config.diffusive[0] = float(
            self.txt_diffusive_min.Value)

        self.Parent.diffusivity.config.sub_diffusive[1] = float(
            self.txt_diffusive_min.Value)-.001

        self.txt_subdiffusive_max.SetValue(
            f"{self.Parent.diffusivity.config.sub_diffusive[1]}")

    def on_active_range_change(self, event):
        self.Parent.diffusivity.config.active[0] = float(
            self.txt_active_min.Value)

        self.Parent.diffusivity.config.diffusive[1] = float(
            self.txt_active_min.Value)-.001

        self.txt_diffusive_max.SetValue(
            f"{self.Parent.diffusivity.config.diffusive[1]}")

    def on_save_diffusivity(self, event):
        self.Parent.statusBar.SetStatusText("Saving changes...")
        self.Parent.diffusivity.update(self.Parent.diffusivity.config)
        self.Destroy()

    def on_cancel_diffusivity(self, event):
        self.Parent.statusBar.SetStatusText("Canceling changes...")
        self.Destroy()
