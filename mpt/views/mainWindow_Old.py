#!/home/leandro/.cache/pypoetry/virtualenvs/mpt-XiopSbUN-py3.7/bin/python
# from transportModeSetupWindow import ModeConfig
# import views.transportModeSetupWindow as tm
from mpt.mpt import Analysis, Report
from mpt import database as mptDB
from matplotlib.figure import Figure
# from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
# import sys
import wx
import os
from pathlib import Path, PurePath
# import time
# from numpy import arange, sin, pi
import matplotlib
matplotlib.use('WXAgg')


class LeftPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundColour("lightgray")

        vboxsizer = wx.BoxSizer(wx.VERTICAL)

        self.label = wx.StaticText(
            self, label="Setup panel", style=wx.ALIGN_CENTER)
        vboxsizer.Add(self.label, 0, wx.EXPAND)

        # self.call_button = wx.Button(self, label="Config")
        # self.call_button.Bind(wx.EVT_BUTTON, self.OnModal)
        # self.call_button.Bind(wx.EVT_BUTTON, self.popup)

        self.SetSizer(vboxsizer)

        # self.text_ctrl = wx.TextCtrl(self, pos=(5, 5))
        # self.my_btn = wx.Button(self, label='Open file', pos=(5, 35))


class RightPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.SetBackgroundColour("green")
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.sizer)
        self.Fit()


class Main(wx.Frame):

    def __init__(self):
        # super(MyFrame, self).__init__(parent,
        #                               title=title,
        #                               size=(960, 600),
        #                               style=wx.DEFAULT_FRAME_STYLE & ~(
        #                                 wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        super(Main, self).__init__(parent=None,
                                   title="Multiple Particle Tracking Analysis",
                                   size=(848, 594),
                                   style=wx.DEFAULT_FRAME_STYLE & ~(
                                       wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetIcon(wx.Icon(os.path.join(
            os.getcwd(), "mpt", "assets", "icon.png")))

        splitter = wx.SplitterWindow(self)
        setup_panel = LeftPanel(splitter)
        graph_panel = RightPanel(splitter)
        splitter.SplitVertically(setup_panel, graph_panel)
        splitter.SetMinimumPaneSize(316)

        # self.statusbar = self.CreateStatusBar(1)
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusWidths([500, -1])

        self.Bind(wx.EVT_CLOSE, self.OnExitApp)

        self.start_app()

        self.InitMenu()
        self.Centre()

    def start_app(self):
        DEV = True
        # DEV = False

        if not PurePath.joinpath(Path.home(), '.mpt').exists():
            Path.mkdir(PurePath.joinpath(Path.home(), '.mpt'))
        if not PurePath.joinpath(Path.home(), '.mpt', 'export').exists():
            Path.mkdir(PurePath.joinpath(Path.home(), '.mpt', 'export'))

        if DEV:
            BASE_PATH = os.path.join(os.path.dirname(
                os.path.realpath(__file__)), 'data')
        else:
            BASE_PATH = str(PurePath.joinpath(Path.home(), '.mpt'))

        self.db = mptDB.Database(BASE_PATH)
        self.db.persist()
        self.analysis = Analysis()
        self.analysis.load_config(self.db)

    def OnExitApp(self, event):
        self.Destroy()

    def OnOpen(self, event):
        self.statusbar.SetStatusText("You clicked on 'Open file' menu...")
        self.AddReports(self.db)

    def OnSave(self, event):
        self.statusbar.SetStatusText("You clicked on 'Save results' menu...")

    def OnModeConfig(self, event):
        self.statusbar.SetStatusText(
            "You clicked on 'Diffusivity ranges configuration' menu...")

    def OnAppConfig(self, event):
        self.statusbar.SetStatusText(
            "You clicked on 'App configuration' menu...")

    def OnAnalysisConfig(self, event):
        self.statusbar.SetStatusText(
            "You clicked on 'Analysis range configuration' menu...")

    def OnModeSetup(self, event):
        self.statusbar.SetStatusText(
            "You clicked on 'Diffusivity configuration' menu...")

    def OnAnalyze(self, event):
        self.statusbar.SetStatusText("You clicked on 'Analyze' menu...")

    def OnHelp(self, event):
        self.statusbar.SetStatusText("You clicked on 'Documentation' menu...")

    def OnAbout(self, event):
        self.statusbar.SetStatusText("You clicked on 'About' menu...")

    def ComposeMenu(self, values: dict) -> wx.Menu:
        menu = wx.Menu()
        for key, item in values.items():
            if key == 'separator':
                menu.AppendSeparator()
                continue
            menu_item = menu.Append(item['id'], key)
            if item['function']:
                self.Bind(wx.EVT_MENU, item['function'], menu_item)
        return menu

    def InitMenu(self):
        # ============================================================ Menu bar
        self.menuBar = wx.MenuBar()
        # ============================================================ Menu bar

        # =========================================================== File menu
        file_dict = {
            '&Open file': {'id': wx.ID_OPEN, 'function': self.OnOpen},
            '&Save results': {'id': wx.ID_SAVE, 'function': self.OnSave}
        }
        fileMenu = self.ComposeMenu(file_dict)
        self.menuBar.Append(fileMenu, "&File")
        # =========================================================== File menu

        # ========================================================== Tools menu
        tools_dict = {
            'App configuration': {
                'id': wx.ID_ANY, 'function': self.OnAppConfig},
            'Analysis configuration': {
                'id': wx.ID_ANY, 'function': self.OnAnalysisConfig},
            'Diffusivity ranges configuration': {
                'id': wx.ID_ANY, 'function': self.OnModeConfig},
            # 'Characterization mode setup': {
            #     'id': wx.ID_SETUP, 'function': self.OnModeSetup},
            'Analyze': {
                'id': wx.ID_ANY, 'function': self.OnAnalyze},
        }
        toolsMenu = self.ComposeMenu(tools_dict,)
        self.menuBar.Append(toolsMenu, '&Tools')
        # ========================================================== Tools menu

        # =========================================================== Help menu
        help_dict = {
            '&Documentation': {'id': wx.ID_HELP, 'function': self.OnHelp},
            'separator': None,
            '&About': {'id': wx.ID_ABOUT, 'function': self.OnAbout},
        }
        helpMenu = self.ComposeMenu(help_dict)
        self.menuBar.Append(helpMenu, '&Help')
        # =========================================================== Help menu

        self.SetMenuBar(self.menuBar)

    def LoadReports(self, file_list: list) -> list:
        report_list = []
        for file in file_list:
            new_report = Report()

            new_report.full_path = file
            new_report.folder_path = os.path.dirname(file)
            new_report.file_name, new_report.extension = os.path.splitext(
                os.path.basename(file))
            full_data = new_report.load_data()
            new_report.raw_data = new_report.clean_data(full_data)

            report_list.append(new_report)

            del new_report
        return report_list

    def AddReports(self, db: mptDB.Database) -> None:
        """Adds one or more 'ImageJ Full Report' file (in .csv format) to a \
            list of reports to be analyzed.
        If the user cancels the operation, nothing is done.
        """
        with wx.FileDialog(None, "Open ImageJ Full report file(s)",
                           wildcard="ImageJ full report files (*.csv)|*.csv",
                           style=wx.FD_OPEN | wx.FD_MULTIPLE) as fileDialog:

            fileDialog.SetDirectory(self.analysis.open_path)
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                print("No file selected...")
                return None

            file_list = fileDialog.GetPaths()
            self.analysis.report_list = self.LoadReports(file_list)

            new_app_config = (fileDialog.GetDirectory(),
                              self.analysis.out_path)
            self.db.update_app_config(new_app_config)


if __name__ == '__main__':
    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop()
