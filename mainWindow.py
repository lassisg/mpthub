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
    # def __init__(self, parent, title):

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

        # self.panel = MyPanel(self)

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
        # dlg = ModeConfig()
        # dlg.ShowModal()
        # if dlg.save:
        #     print("Saving")
        #     # self.log.AppendText("Name: "+dlg.result_name+"\n")
        #     # self.log.AppendText("Surname: "+dlg.result_surname+"\n")
        #     # self.log.AppendText("Nickname: "+dlg.result_nickname+"\n")
        # else:
        #     print("Not saving")
        #     # self.log.AppendText("No Input found\n")
        # dlg.Destroy()

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


class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)

        self.cfg_label = wx.StaticText(self, label="a", pos=(760, 520))
        self.text_ctrl = wx.TextCtrl(self, pos=(5, 5))
        self.my_btn = wx.Button(self, label='Open file', pos=(5, 35))
        # self.my_btn.Bind(wx.EVT_BUTTON, self.OnEdit)

    # def OnOpen(self, event):
        # self.text_ctrl.SetValue('OnOpen')

        # if self.contentNotSaved:
        #     if wx.MessageBox("Current content has not been saved! Proceed?",
        #                      "Please confirm",
        #                      wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
        #         return

        #     otherwise ask the user what new file to open

        # with wx.FileDialog(self, "Open XYZ file",
        #                    wildcard="XYZ files (*.xyz)|*.xyz",
        #                    style=wx.FD_OPEN |
        #                          wx.FD_FILE_MUST_EXIST) as fileDialog:

        #     if fileDialog.ShowModal() == wx.ID_CANCEL:
        #         return     # the user changed their mind

        #     # Proceed loading the file chosen by the user
        #     pathname = fileDialog.GetPath()
        #     try:
        #         with open(pathname, 'r') as file:
        #             self.doLoadDataOrWhatever(file)
        #     except IOError:
        #         wx.LogError("Cannot open file '%s'." % newfile)

    # def OnOpenFolder(self, event):
        # self.text_ctrl.SetValue('OnOpenFolder')
        # if self.contentNotSaved:
        #     if wx.MessageBox("Current content has not been saved! Proceed?",
        #                      "Please confirm",
        #                      wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
        #         return

        # # otherwise ask the user what new file to open
        # with wx.DirDialog(None, "Choose input directory", "",
        #                   wx.DD_DEFAULT_STYLE |
        #                   wx.DD_DIR_MUST_EXIST) as dirDialog:
        #     if dirDialog.ShowModal() == wx.ID_CANCEL:
        #         return

        #     # Proceed loading the folder chosen by the user
        #     videoPath = str(dirDialog.GetPath())
        #     videoPath = str.replace(videoPath, "\\", "/")
        #     print(videoPath)

        #     entries = os.scandir(videoPath)
        #     imageList = []
        #     try:
        #         with os.scandir(videoPath) as entries:
        #             for entry in entries:
        #                 extension = os.path.splitext(entry.name)[1]
        #                 if entry.is_file() and extension == ".tif":
        #                     # print(f"{entry.name} -> {extension}")
        #                     fileName = os.path.splitext(entry.name)[0]
        #                     imageList.append(fileName)

        #         doAnalysis = wx.MessageBox(
        #             "Would you like to start the video analysis on ImageJ?",
        #             "Image Analysis", wx.YES_NO | wx.CENTRE)

        #         if doAnalysis == wx.YES:
        #             print("Let's do it!")
        #         reportPath = f"{videoPath}/reports"
        #         if not os.path.exists(reportPath):
        #             os.mkdir(reportPath)
        #         fiji = ic()
        #         fiji.startAnalysis(imageList, videoPath, reportPath)
        #         else:
        #             print("No worries, we'll do it another time!")

        #     except IOError:
        #         wx.LogError("Cannot read folder")

    # def OnSave(self, event):
        # self.text_ctrl.SetValue('OnSave')

    # def OnQuit(self, event):
        # self.Close()

    # def OnHelp(self, event):
        # self.text_ctrl.SetValue('OnHelp')

    # def OnAbout(self, event):
        # self.text_ctrl.SetValue('OnAbout')

    # def OnEdit(self, event):
        # self.text_ctrl.SetValue('OnEdit')
        # start = time.time()
        # self.OnOpenFolder(event)
        # end = time.time()
        # print(f"Elapsed time: {end-start}")

        # class ModeConfig(wx.Dialog):
        # _CFG_PATH = os.getcwd() + '/src/res/'

    # def __init__(self):
        # wx.Dialog.__init__(self, None, -1,
        #                    "Characterization mode setup", size=(356, 224))

        # self.save = False
        # # self.transport_mode_values = self.GetTransportMode()

        # # TODO: Bind OnChange event for fields
        # x_pos = 65
        # y_pos = 16
        # self.active_values = self.transport_mode_values["active_range"]
        # self.active_range = wx.StaticText(
        #     self, label="Active", pos=(x_pos, y_pos+4))
        # self.active_from = wx.NumCtrl(
        #     self, value=self.active_values[0], fractionWidth=1, pos=(
        #         x_pos+100, y_pos), size=(30, -1), autoSize=False)
        # self.active_signal = wx.StaticText(
        #     self, label="+", pos=(x_pos+130, y_pos+3))

        # y_pos += 30
        # self.dif_values = self.transport_mode_values["diffusive_range"]
        # self.dif_range = wx.StaticText(
        #     self, label="Diffusive", pos=(x_pos, y_pos+4))
        # self.dif_from = wx.NumCtrl(
        #     self, value=self.dif_values[0], fractionWidth=1, pos=(
        #         x_pos+100, y_pos), size=(30, -1), autoSize=False)
        # self.dif_signal = wx.StaticText(
        #     self, label="->", pos=(x_pos+135, y_pos+4))
        # self.dif_to = wx.NumCtrl(
        #     self, value=self.dif_values[1], fractionWidth=3, pos=(
        #         x_pos+150, y_pos), size=(40, -1), autoSize=False)
        # self.dif_to.Disable()

        # y_pos += 30
        # self.subdif_values = self.transport_mode_values["sub-diffusive_range"]
        # self.subdif_range = wx.StaticText(
        #     self, label="Subdiffusive", pos=(x_pos, y_pos+4))
        # self.subdif_from = wx.NumCtrl(
        #     self, value=self.subdif_values[0], fractionWidth=1, pos=(
        #         x_pos+100, y_pos), size=(30, -1), autoSize=False)
        # self.subdif_signal = wx.StaticText(
        #     self, label="->", pos=(x_pos+135, y_pos+4))
        # self.subdif_to = wx.NumCtrl(
        #     self, value=self.subdif_values[1], fractionWidth=3, pos=(
        #         x_pos+150, y_pos), size=(40, -1), autoSize=False)
        # # self.subdif_to = wx.TextCtrl(self, value=f'{self.subdif_values[1]}',
        # #                              style=wx.TE_CENTRE,
        # #                              pos=(x_pos+150, y_pos), size=(50, -1))
        # self.subdif_to.Disable()

        # y_pos += 30
        # self.immobile_values = self.transport_mode_values["immobile_range"]
        # self.immobile_range = wx.StaticText(
        #     self, label="Immobile", pos=(x_pos, y_pos+4))
        # self.immobile_from = wx.NumCtrl(self,
        #                                 value=self.immobile_values[0],
        #                                 fractionWidth=1,
        #                                 pos=(x_pos+100, y_pos),
        #                                 size=(30, -1),
        #                                 autoSize=False)
        # self.immobile_signal = wx.StaticText(self, label="->",
        #                                      pos=(x_pos+135, y_pos+4))
        # self.immobile_to = wx.NumCtrl(self, value=self.immobile_values[1],
        #                               fractionWidth=3,
        #                               pos=(x_pos+150, y_pos),
        #                               size=(40, -1),
        #                               autoSize=False)
        # self.immobile_to = wx.TextCtrl(self,
        #                                value=f'{self.immobile_values[1]}',
        #                                style=wx.TE_CENTRE,
        #                                pos=(x_pos+150, y_pos),
        #                                size=(50, -1))
        # self.immobile_from.Disable()
        # self.immobile_to.Disable()

        # y_pos += 25
        # self.saveButton = wx.Button(self, label="Save", pos=(135, y_pos+13))
        # self.saveButton.Bind(wx.EVT_BUTTON, self.SaveConnString)

        # self.closeButton = wx.Button(self, label="Cancel", pos=(237, y_pos+13))
        # self.closeButton.Bind(wx.EVT_BUTTON, self.OnQuit)

        # self.Bind(wx.EVT_CLOSE, self.OnQuit)
        # self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUp)
        # self.Centre()
        # self.Show()

    # def OnQuit(self, event):
        # print("Closing without saving changes.")
        # self.Destroy()

    # def OnKeyUp(self, event):

        # key_code = event.GetKeyCode()
        # if key_code == wx.WXK_ESCAPE:
        #     self.OnQuit(wx.EVT_BUTTON)
        #     self.Destroy()
        # elif key_code == wx.WXK_RETURN:
        #     self.SaveConnString(wx.EVT_BUTTON)
        #     self.Destroy()

        # self.dif_to.SetValue(self.GetLimitValue(self.active_from.GetValue()))
        # self.subdif_to.SetValue(self.GetLimitValue(self.dif_from.GetValue()))
        # self.immobile_to.SetValue(
        #     self.GetLimitValue(self.subdif_from.GetValue()))

        # event.Skip()

    # def GetTransportMode(self, full: bool = False, *part: dict) -> dict:

        # with open(self._CFG_PATH + 'mpt-config.json') as fh:
        #     config = json.load(fh)
        #     if full and part:
        #         new_config = {}
        #         print(f"\nUsing for Set!\n")
        #         for config_group in config:
        #             if config_group not in "transport_mode":
        #                 new_config[config_group] = config[config_group]
        #                 print(config[config_group])
        #                 print(new_config[config_group])

        #         print(part)
        #     else:
        #         if ("transport_mode" in config):
        #             return config["transport_mode"]

        # return config

    # def SetTransportMode(self, json_string: dict):
        # self.GetTransportMode(True, self.transport_mode_values)
        # print("Set transport mode!")

        # return None

    # def GetLimitValue(self, value: float) -> str:
        # limit_value = value - 0.001
        # return limit_value

    # def SaveConnString(self, event):
        # print("Save changes!")
        # self.save = True
        # self.GetLimitValue(self.active_from.GetValue())
        # new_active_from = self.active_from.GetValue()

        # new_dif_from = self.dif_from.GetValue()
        # new_dif_to = float(f'{new_active_from - 0.001:.3f}')

        # new_subdif_from = self.subdif_from.GetValue()
        # new_subdif_to = float(f'{new_dif_from - 0.001:.3f}')

        # new_immobile_from = self.immobile_from.GetValue()
        # new_immobile_to = float(f'{new_subdif_from - 0.001:.3f}')

        # transport_mode = {
        #     "immobile_range": [new_immobile_from, new_immobile_to],
        #     "sub-diffusive_range": [new_subdif_from, new_subdif_to],
        #     "diffusive_range": [new_dif_from, new_dif_to],
        #     "active_range": [new_active_from]
        # }
        # self.SetTransportMode(self.transport_mode_values)
        # self.Destroy()


if __name__ == '__main__':
    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop()
