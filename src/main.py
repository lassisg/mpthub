from mpt.mpt import MPT
import os
# import time

# Initial setup
CFG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'data')


if __name__ == '__main__':
    # app = mptApp()
    # app = wx.App()
    # frame = Main()
    # frame.Show()
    # app.MainLoop()

    # start_time = time.time()

    # TODO: Code below must go to GUI
    analysis = MPT(CFG_PATH)
    analysis.add_report()
    analysis.analyze()
    analysis.export()
    # analysis.end()

    # end_time = time.time()
    # print(f"Elapsed time: {end_time-start_time}")
