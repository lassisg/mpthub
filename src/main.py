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
    analysis.add_file()
    # analysis.to_string()
    analysis.get_trajectories()
    analysis.filter_trajectories()
    analysis.refine_trajectories()
    analysis.analyze_trajectories()

    print(analysis.trajectories.head())
    print(analysis.trajectories.describe())

    # analysis.start_analysis()
    # analysis.end()
