import wx
from mpt.views.mainWindow import mainWindow
from mpt.database import Database
from pathlib import Path
from dynaconf import settings


def resolve_paths() -> None:
    if not Path(settings.BASE_PATH).exists():
        Path.mkdir(Path(settings.BASE_PATH))

    if not Path(settings.EXPORT_PATH).exists():
        Path.mkdir(Path(settings.EXPORT_PATH))


if __name__ == "__main__":

    resolve_paths()
    db = Database()
    mpt_app = wx.App()
    frame = mainWindow(parent=None)
    frame.Show(True)
    mpt_app.MainLoop()
