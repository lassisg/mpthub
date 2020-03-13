# import sqlite3
import mpt
# from mpt import database as db
from mpt.mpt import Analysis
from mpt.database import Database
import os
import time

# Initial setup
CFG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'data')
DB_PATH = os.path.join(CFG_PATH, 'config.db')


def main():
    # app = mptApp()
    # app = wx.App()
    # frame = Main()
    # frame.Show()
    # app.MainLoop()

    db = Database(DB_PATH)
    db.persist()

    # TODO: Code below must go to GUI
    analysis = Analysis(CFG_PATH)
    analysis.load_config(db)
    analysis.add_report()
    if analysis.report_list:
        analysis.analyze()
        analysis.export()

    db.conn.close()


if __name__ == '__main__':
    # start_time = time.time()
    main()
    # end_time = time.time()
    # print(f"Elapsed time: {end_time-start_time}")
