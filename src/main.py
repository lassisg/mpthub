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
    all_trajectories = analysis.get_trajectories()
    filtered_trajectories = analysis.filter_trajectories()
    print(all_trajectories.describe())
    # analysis.start_analysis()
    # analysis.end()

#                    y  ...       particle
# count  110469.000000  ...  110469.000000
# mean      249.555499  ...    3510.637835
# std       148.334778  ...    2741.546716
# min         3.860086  ...       0.000000
# 25%       121.220245  ...     849.000000
# 50%       247.328968  ...    3213.000000
# 75%       382.074834  ...    5862.000000
# max       507.008384  ...    9151.000000
