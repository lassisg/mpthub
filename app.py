import wx
from mpt.views.mainWindow import mainWindow


if __name__ == "__main__":
    mpt_app = wx.App()
    frame = mainWindow(parent=None)
    frame.Show(True)
    mpt_app.MainLoop()
