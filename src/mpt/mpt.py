# from mpt.analysis import Analysis
from mpt.video import Video
import mpt.utils as mpt_utils
import tkinter as tk
from tkinter import filedialog
import os
import trackpy as tp
import pandas as pd
import matplotlib
matplotlib.use('WXAgg')


class MPT():
    # fps = 30      # Get from microscopy configuration
    msd = pd.DataFrame()
    deff = pd.DataFrame()
    videos = []

    def __init__(self, config_path: str):
        super().__init__()
        self.config_path = config_path
        self.out_path = os.path.join(self.config_path, 'export')
        self.name = ""
        self.fileName = ""
        self.videos = []
        self.msd = pd.DataFrame()
        self.deff = pd.DataFrame()
        self.diffusivity = 0
        self.feature_size = 11
        self.min_frame_seq = 560

    def addVideos(self) -> None:
        root = tk.Tk()
        root.withdraw()

        file_list = filedialog.askopenfilenames()

        if not file_list:
            print("No file selected...")
            return None

        for file in file_list:
            new_video = Video()

            new_video.full_path = file
            new_video.path = os.path.dirname(file)
            new_video.name, new_video.extension = os.path.splitext(
                os.path.basename(file))
            new_video.config_path = self.config_path
            new_video.get_data()
            self.videos.append(new_video)

            del new_video

    def start_analysis(self):
        for video in self.videos:
            video.preview()
            tp.annotate(video.features, video.frames[0])

            # TODO: Add decision and config for batch locate
            video.analyze()

            if video.trajectories['particle'].nunique() > 0:
                video.refine()
                video.analyze_trajectories()
                video.get_MSD()

                self.get_full_MSD(video.msd)

                video.get_EMSD()

                video.get_Deff()
                video.msd = mpt_utils.rename_columns(video.msd)
                video.deff = mpt_utils.rename_columns(video.deff)

                # Individual Particle Analysis report ------
                mpt_utils.export_individual_particle_analysis(video,
                                                              self.out_path)

                # Transport Mode Characterization report ----
                mpt_utils.export_transport_mode(video, self.out_path)

    def get_full_MSD(self, new_msd):
        self.msd = pd.concat([self.msd, new_msd],
                             axis=1,
                             ignore_index=True,
                             sort=False)

    # def end(self) -> None:
        # print(self.analysis)
        # del self.analysis
