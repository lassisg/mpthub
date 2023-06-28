from pathlib import Path
import os
import sys


class Settings():
    def __init__(self) -> None:

        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(
                Path(os.path.abspath(__file__)).parent)

        self.APP_PATH = application_path
        self.ICON_PATH = os.path.join(self.APP_PATH, "mpt", "assets")
        self.DB_NAME = 'config.db'
        self.BASE_PATH = Path.joinpath(Path.home(), ".mpt")
        self.DB_PATH = Path.joinpath(self.BASE_PATH, self.DB_NAME)
        self.EXPORT_PATH = Path.joinpath(self.BASE_PATH, "export")

        self.DEFAULT_OPEN_FOLDER = f"{Path.home()}"
        self.DEFAULT_SAVE_FOLDER = f"{Path.home()}"

        self.DEFAULT_IMMOBILE_MIN = 0.000
        self.DEFAULT_SUB_DIFFUSIVE_MIN = 0.200
        self.DEFAULT_DIFFUSIVE_MIN = 0.900
        self.DEFAULT_ACTIVE_MIN = 1.200

        self.DEFAULT_IMMOBILE_MAX = 0.199
        self.DEFAULT_SUB_DIFFUSIVE_MAX = 0.899
        self.DEFAULT_DIFFUSIVE_MAX = 1.199

        self.DEFAULT_P_SIZE = 200
        self.DEFAULT_MIN_FRAMES = 590
        self.DEFAULT_FPS = 30
        self.DEFAULT_DELTA_T = 33.00
        self.DEFAULT_TOTAL_FRAMES = 606
        self.DEFAULT_WIDTH_PX = 512
        self.DEFAULT_WIDTH_SI = 160.00
        self.DEFAULT_TIME = 10.00
        self.DEFAULT_TEMPERATURE_C = 37.00
