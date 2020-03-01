from mpt.mpt import MPT_Full
import os
import timeit

# Initial setup
CFG_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'data')


def execute_all():
    # TODO: Code below must go to GUI
    analysis = MPT_Full(CFG_PATH)
    analysis.add_file()
    # analysis.to_string()
    if analysis.file_list:
        analysis.get_trajectories()

        for partial in analysis.file_list:
            if not partial.trajectories.empty:
                partial.filter_trajectories()
                # partial.refine_trajectories()
                # partial.analyze_trajectories()

        # if not analysis.trajectories.empty:
        #     analysis.filter_trajectories()
        #     analysis.refine_trajectories()
        #     analysis.analyze_trajectories()
    # else:
    #     print("No file selected...")
        # print(analysis.trajectories.head())
        # print(analysis.trajectories.describe())

        # analysis.start_analysis()
        # analysis.end()


if __name__ == '__main__':
    # app = mptApp()
    # app = wx.App()
    # frame = Main()
    # frame.Show()
    # app.MainLoop()
    print(timeit.timeit(execute_all, number=1))
    print("Done")
