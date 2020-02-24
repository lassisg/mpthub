# from transportModeSetupWindow import ModeConfig
import views.transportModeSetupWindow as tm
from matplotlib.figure import Figure
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import sys
import wx
import os
import time
from numpy import arange, sin, pi
import matplotlib
matplotlib.use('WXAgg')

# sys.path.append("D:/Cloud/Onedrive/Pessoal/Acadêmico/FEUP/2019-2020-PDISS_DISS/App/src/res/")
# from ic import ic


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
        # super(MyFrame, self).__init__(parent, title=title, size=(960, 600),style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        super(Main, self).__init__(parent=None, title="Multiple Particle Tracking Analysis", size=(
            848, 594), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.SetIcon(wx.Icon(os.path.join(
            os.getcwd(), "src", "img", "icon.png")))

        splitter = wx.SplitterWindow(self)
        setup_panel = LeftPanel(splitter)
        graph_panel = RightPanel(splitter)
        splitter.SplitVertically(setup_panel, graph_panel)
        splitter.SetMinimumPaneSize(316)

        # self.panel = MyPanel(self)

        # self.statusbar = self.CreateStatusBar(1)
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusWidths([500, -1])

        self.InitMenu()
        self.Centre()

    def OnNew(self, event):
        self.statusbar.SetStatusText("You clicked on 'New' menu...")

    def OnOpen(self, event):
        self.statusbar.SetStatusText("You clicked on 'Open' menu...")

    def OnOpenFolder(self, event):
        self.statusbar.SetStatusText("You clicked on 'Open Folder' menu...")

    def OnSave(self, event):
        self.statusbar.SetStatusText("You clicked on 'Save' menu...")

    def OnModeSetup(self, event):
        self.statusbar.SetStatusText(
            "You clicked on 'Characterization mode setup' menu...")
        dlg = tm.ModeConfig()
        dlg.ShowModal()
        if dlg.save:
            print("Saving")
        #     self.log.AppendText("Name: "+dlg.result_name+"\n")
        #     self.log.AppendText("Surname: "+dlg.result_surname+"\n")
        #     self.log.AppendText("Nickname: "+dlg.result_nickname+"\n")
        else:
            print("Not saving")
        #     self.log.AppendText("No Input found\n")
        dlg.Destroy()

    def InitMenu(self):
        # ============================================================ Menu bar
        self.menuBar = wx.MenuBar()
        # ============================================================ Menu bar

        # =========================================================== File menu
        fileMenu = wx.Menu()
        file_dict = {
            '&New': {'id': wx.ID_NEW, 'function': self.OnNew},
            '&Open': {'id': wx.ID_OPEN, 'function': self.OnOpen},
            'Open &Directory': {'id': wx.ID_FILEDLGG, 'function': self.OnOpenFolder},
            '&Save': {'id': wx.ID_SAVE, 'function': self.OnSave}
        }
        for key, item in file_dict.items():
            fileMenu.Append(item['id'], key)
            if item['function']:
                self.Bind(wx.EVT_MENU, item['function'], id=item['id'])

        fileMenu.AppendSeparator()

        # ====================================================== Import submenu
        importSubMenu = wx.Menu()
        import_dict = {
            'Import newsfeed list...': {'id': wx.ID_ANY, 'function': ''},
            'Import bookmarks...': {'id': wx.ID_ANY, 'function': ''},
            'Import mail...': {'id': wx.ID_ANY, 'function': ''},
        }
        for key, item in import_dict.items():
            importSubMenu.Append(item['id'], key)
            if item['function']:
                self.Bind(wx.EVT_MENU, item['function'], id=item['id'])

        fileMenu.AppendSubMenu(importSubMenu, 'I&mport')
        self.menuBar.Append(fileMenu, "&File")
        # =========================================================== File menu

        # ========================================================== Tools menu
        toolsMenu = wx.Menu()

        toolsMenu.Append(wx.ID_SETUP, 'Characterization mode setup')
        self.Bind(wx.EVT_MENU, self.OnModeSetup, id=wx.ID_SETUP)

        self.menuBar.Append(toolsMenu, '&Tools')
        # ========================================================== Tools menu

        # =========================================================== Help menu
        helpMenu = wx.Menu()

        helpMenu.Append(wx.ID_HELP, '&Documentation')
        # self.Bind(wx.EVT_MENU, self.OnHelp, id=wx.ID_HELP)

        helpMenu.AppendSeparator()

        helpMenu.Append(wx.ID_ABOUT, '&About')
        # self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)

        self.menuBar.Append(helpMenu, '&Help')
        # =========================================================== Help menu

        self.SetMenuBar(self.menuBar)


class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)

        self.cfg_label = wx.StaticText(self, label="a", pos=(760, 520))
        self.text_ctrl = wx.TextCtrl(self, pos=(5, 5))
        self.my_btn = wx.Button(self, label='Open file', pos=(5, 35))
        # self.my_btn.Bind(wx.EVT_BUTTON, self.OnEdit)

    # def OnOpen(self, event):
    #     self.text_ctrl.SetValue('OnOpen')

#         # if self.contentNotSaved:
#         #     if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm", wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
#         #         return

#         # otherwise ask the user what new file to open
#         # with wx.FileDialog(self, "Open XYZ file", wildcard="XYZ files (*.xyz)|*.xyz",
#         #                    style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

#         #     if fileDialog.ShowModal() == wx.ID_CANCEL:
#         #         return     # the user changed their mind

#         #     # Proceed loading the file chosen by the user
#         #     pathname = fileDialog.GetPath()
#         #     try:
#         #         with open(pathname, 'r') as file:
#         #             self.doLoadDataOrWhatever(file)
#         #     except IOError:
#         #         wx.LogError("Cannot open file '%s'." % newfile)

    # def OnOpenFolder(self, event):
    #     self.text_ctrl.SetValue('OnOpenFolder')
        # if self.contentNotSaved:
        #     if wx.MessageBox("Current content has not been saved! Proceed?", "Please confirm", wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
        #         return

        # otherwise ask the user what new file to open
        # with wx.DirDialog(None, "Choose input directory", "",
        #                   wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dirDialog:
        #     if dirDialog.ShowModal() == wx.ID_CANCEL:
        #         return

        #     # Proceed loading the folder chosen by the user
        #     videoPath = str(dirDialog.GetPath())
        #     videoPath = str.replace(videoPath, "\\", "/")
        #     print(videoPath)

        #     entries = os.scandir(videoPath)
        #     imageList = []
        #     # try:
        #     #     with os.scandir(videoPath) as entries:
        #     #         for entry in entries:
        #     #             extension = os.path.splitext(entry.name)[1]
        #     #             if entry.is_file() and extension == ".tif":
        #     #                 # print(f"{entry.name} -> {extension}")
        #     #                 fileName = os.path.splitext(entry.name)[0]
        #     #                 imageList.append(fileName)

        #     #     # doAnalysis = wx.MessageBox("Would you like to start the video analysis on ImageJ?",
        #     #     #                            "Image Analysis", wx.YES_NO | wx.CENTRE)

        #     #     # if doAnalysis == wx.YES:
        #     #     #     print("Let's do it!")
        #     #         # reportPath = f"{videoPath}/reports"
        #     #     #     if not os.path.exists(reportPath):
        #     #     #         os.mkdir(reportPath)
        #     #         # fiji = ic()
        #     #         # fiji.startAnalysis(imageList, videoPath, reportPath)
        #     #     # else:
        #     #     #     print("No worries, we'll do it another time!")

        #     # except IOError:
        #     #     wx.LogError("Cannot read folder")

    # def OnSave(self, event):
    #     self.text_ctrl.SetValue('OnSave')

#     def OnQuit(self, event):
#         self.Close()

#     def OnHelp(self, event):
#         self.text_ctrl.SetValue('OnHelp')

#     def OnAbout(self, event):
#         self.text_ctrl.SetValue('OnAbout')

#     def OnEdit(self, event):
#         self.text_ctrl.SetValue('OnEdit')
#         start = time.time()
#         self.OnOpenFolder(event)
#         end = time.time()
#         print(f"Elapsed time: {end-start}")


# class ModeConfig(wx.Dialog):
#     _CFG_PATH = os.getcwd() + '/src/res/'

#     def __init__(self):
#         wx.Dialog.__init__(
#             self, None, -1, "Characterization mode setup", size=(356, 224))

#         self.save = False
#         self.transport_mode_values = self.GetTransportMode()

#         # TODO: Bind OnChange event for fields
#         x_pos = 65
#         y_pos = 16
#         self.active_values = self.transport_mode_values["active_range"]
#         self.active_range = wx.StaticText(
#             self, label="Active", pos=(x_pos, y_pos+4))
#         self.active_from = NumCtrl(self, value=self.active_values[0], fractionWidth=1, pos=(
#             x_pos+100, y_pos), size=(30, -1), autoSize=False)
#         self.active_signal = wx.StaticText(
#             self, label="+", pos=(x_pos+130, y_pos+3))

#         y_pos += 30
#         self.dif_values = self.transport_mode_values["diffusive_range"]
#         self.dif_range = wx.StaticText(
#             self, label="Diffusive", pos=(x_pos, y_pos+4))
#         self.dif_from = NumCtrl(self, value=self.dif_values[0], fractionWidth=1, pos=(
#             x_pos+100, y_pos), size=(30, -1), autoSize=False)
#         self.dif_signal = wx.StaticText(
#             self, label="->", pos=(x_pos+135, y_pos+4))
#         self.dif_to = NumCtrl(self, value=self.dif_values[1], fractionWidth=3, pos=(
#             x_pos+150, y_pos), size=(40, -1), autoSize=False)
#         self.dif_to.Disable()

#         y_pos += 30
#         self.subdif_values = self.transport_mode_values["sub-diffusive_range"]
#         self.subdif_range = wx.StaticText(
#             self, label="Subdiffusive", pos=(x_pos, y_pos+4))
#         self.subdif_from = NumCtrl(self, value=self.subdif_values[0], fractionWidth=1, pos=(
#             x_pos+100, y_pos), size=(30, -1), autoSize=False)
#         self.subdif_signal = wx.StaticText(
#             self, label="->", pos=(x_pos+135, y_pos+4))
#         self.subdif_to = NumCtrl(self, value=self.subdif_values[1], fractionWidth=3, pos=(
#             x_pos+150, y_pos), size=(40, -1), autoSize=False)
#         # self.subdif_to = wx.TextCtrl(self, value=f'{self.subdif_values[1]}', style=wx.TE_CENTRE, pos=(x_pos+150, y_pos), size=(50, -1))
#         self.subdif_to.Disable()

#         y_pos += 30
#         self.immobile_values = self.transport_mode_values["immobile_range"]
#         self.immobile_range = wx.StaticText(
#             self, label="Immobile", pos=(x_pos, y_pos+4))
#         self.immobile_from = NumCtrl(self, value=self.immobile_values[0], fractionWidth=1, pos=(
#             x_pos+100, y_pos), size=(30, -1), autoSize=False)
#         self.immobile_signal = wx.StaticText(
#             self, label="->", pos=(x_pos+135, y_pos+4))
#         self.immobile_to = NumCtrl(self, value=self.immobile_values[1], fractionWidth=3, pos=(
#             x_pos+150, y_pos), size=(40, -1), autoSize=False)
#         # self.immobile_to = wx.TextCtrl(self, value=f'{self.immobile_values[1]}', style=wx.TE_CENTRE, pos=(x_pos+150, y_pos), size=(50, -1))
#         self.immobile_from.Disable()
#         self.immobile_to.Disable()

#         y_pos += 25
#         self.saveButton = wx.Button(self, label="Save", pos=(135, y_pos+13))
#         self.saveButton.Bind(wx.EVT_BUTTON, self.SaveConnString)

#         self.closeButton = wx.Button(self, label="Cancel", pos=(237, y_pos+13))
#         self.closeButton.Bind(wx.EVT_BUTTON, self.OnQuit)

#         self.Bind(wx.EVT_CLOSE, self.OnQuit)
#         self.Bind(wx.EVT_CHAR_HOOK, self.OnKeyUp)
#         self.Centre()
#         self.Show()

#     def OnQuit(self, event):
#         print("Closing without saving changes.")
#         self.Destroy()

#     def OnKeyUp(self, event):

#         key_code = event.GetKeyCode()
#         if key_code == wx.WXK_ESCAPE:
#             self.OnQuit(wx.EVT_BUTTON)
#             self.Destroy()
#         elif key_code == wx.WXK_RETURN:
#             self.SaveConnString(wx.EVT_BUTTON)
#             self.Destroy()

#         self.dif_to.SetValue(self.GetLimitValue(self.active_from.GetValue()))
#         self.subdif_to.SetValue(self.GetLimitValue(self.dif_from.GetValue()))
#         self.immobile_to.SetValue(
#             self.GetLimitValue(self.subdif_from.GetValue()))

#         event.Skip()

#     def GetTransportMode(self, full: bool = False, *part: dict) -> dict:

#         with open(self._CFG_PATH + 'mpt-config.json') as fh:
#             config = json.load(fh)
#             if full and part:
#                 new_config = {}
#                 print(f"\nUsing for Set!\n")
#                 for config_group in config:
#                     if config_group not in "transport_mode":
#                         new_config[config_group] = config[config_group]
#                         print(config[config_group])
#                         print(new_config[config_group])

#                 print(part)
#             else:
#                 if ("transport_mode" in config):
#                     return config["transport_mode"]

#         return config

#     def SetTransportMode(self, json_string: dict):
#         self.GetTransportMode(True, self.transport_mode_values)
#         print("Set transport mode!")

#         return None

#     def GetLimitValue(self, value: float) -> str:
#         limit_value = value - 0.001
#         return limit_value

#     def SaveConnString(self, event):
#         print("Save changes!")
#         self.save = True
#         # self.GetLimitValue(self.active_from.GetValue())
#         # new_active_from = self.active_from.GetValue()

#         # new_dif_from = self.dif_from.GetValue()
#         # new_dif_to = float(f'{new_active_from - 0.001:.3f}')

#         # new_subdif_from = self.subdif_from.GetValue()
#         # new_subdif_to = float(f'{new_dif_from - 0.001:.3f}')

#         # new_immobile_from = self.immobile_from.GetValue()
#         # new_immobile_to = float(f'{new_subdif_from - 0.001:.3f}')

#         # transport_mode = {
#         #     "immobile_range": [new_immobile_from, new_immobile_to],
#         #     "sub-diffusive_range": [new_subdif_from, new_subdif_to],
#         #     "diffusive_range": [new_dif_from, new_dif_to],
#         #     "active_range": [new_active_from]
#         # }
#         # self.SetTransportMode(self.transport_mode_values)
#         self.Destroy()


class mptApp(wx.App):
    def OnInit(self):
        self.frame = Main(
            parent=None, title="Multiple Particle Tracking Analysis")
        self.frame.Show()
        return True


# For dev use only ------------------------------------------------------------
if __name__ == '__main__':
    # app = mptApp()
    app = wx.App()
    frame = Main()
    frame.Show()
    app.MainLoop()
