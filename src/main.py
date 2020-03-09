from mpt.mpt import MPT
import os
# Initial setup
CFG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'data')


if __name__ == '__main__':
    # app = mptApp()
    # app = wx.App()
    # frame = Main()
    # frame.Show()
    # app.MainLoop()

    # TODO: Code below must go to GUI
    analysis = MPT(CFG_PATH)
    analysis.add_report()
    analysis.analyze()
    # analysis.end()
