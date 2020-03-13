# import sqlite3
import mpt
# from mpt import database as db
from mpt.mpt import Analysis
from mpt.database import Database
import os
import time
from pathlib import Path, PurePath

DEV = True


def main():
    if not PurePath.joinpath(Path.home(), '.mpt').exists():
        Path.mkdir(PurePath.joinpath(Path.home(), '.mpt'))
    if not PurePath.joinpath(Path.home(), '.mpt', 'export').exists():
        Path.mkdir(PurePath.joinpath(Path.home(), '.mpt', 'export'))

    if DEV:
        BASE_PATH = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'data')
    else:
        BASE_PATH = str(PurePath.joinpath(Path.home(), '.mpt'))

    DB_PATH = os.path.join(BASE_PATH, 'config.db')
    OUT_PATH = os.path.join(BASE_PATH, 'export')
    # app = mptApp()
    # app = wx.App()
    # frame = Main()
    # frame.Show()
    # app.MainLoop()

    db = Database(DB_PATH)
    db.persist(BASE_PATH)

    # TODO: Code below must go to GUI
    analysis = Analysis(OUT_PATH)
    analysis.load_config(db)
    analysis.add_report(db)
    if analysis.report_list:
        analysis.analyze()
        analysis.export()

    db.conn.close()


if __name__ == '__main__':
    # start_time = time.time()
    main()
    # end_time = time.time()
    # print(f"Elapsed time: {end_time-start_time}")
