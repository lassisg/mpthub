# import sqlite3
import mpt
# from mpt import database as db
from mpt.mpt import Analysis
from mpt.database import Database
import os
import time
from pathlib import Path, PurePath

# Initial setup
CFG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'data')


def main():
    if not PurePath.joinpath(Path.home(), '.mpt').exists():
        Path.mkdir(PurePath.joinpath(Path.home(), '.mpt'))

    DB_PATH = str(PurePath.joinpath(Path.home(), '.mpt', 'config.db'))

    # app = mptApp()
    # app = wx.App()
    # frame = Main()
    # frame.Show()
    # app.MainLoop()

    db = Database(DB_PATH)
    db.persist()

    # # TODO: Code below must go to GUI
    # analysis = Analysis(CFG_PATH)
    # analysis.load_config(db)
    # analysis.add_report()
    # if analysis.report_list:
    #     analysis.analyze()
    #     analysis.export()

    db.conn.close()


if __name__ == '__main__':
    # start_time = time.time()
    main()
    # end_time = time.time()
    # print(f"Elapsed time: {end_time-start_time}")
    # home = str(Path.home())
