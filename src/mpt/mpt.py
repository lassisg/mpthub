# from mpt.analysis import Analysis
from mpt.analysis import Analysis
import mpt.utils as mpt_utils
import tkinter as tk
from tkinter import filedialog
import os
import trackpy as tp
import pandas as pd
import matplotlib
matplotlib.use('WXAgg')


class MPT():
    def __init__(self, config_path: str):
        super().__init__()
        self.msd = pd.DataFrame()
        self.deff = pd.DataFrame()
        self.config_path = config_path
        self.out_path = os.path.join(self.config_path, 'export')
        self.file_list = []

    def add_file(self) -> None:
        root = tk.Tk()
        root.withdraw()

        file_list = filedialog.askopenfilenames()

        if not file_list:
            print("No file selected...")
            return None

        for file in file_list:
            new_item = Analysis()

            new_item.config_path = self.config_path
            new_item.full_path = file
            new_item.file_path = os.path.dirname(file)
            new_item.file_name, new_item.file_ext = os.path.splitext(
                os.path.basename(file))

            if new_item.file_ext in (".tif", ".tiff"):
                new_item.get_tif_metadata()

            self.file_list.append(new_item)
            del new_item

    def to_string(self):
        print(f"Config. path: {self.config_path}")
        print(f"Export path: {self.out_path}")
        print("Files:")
        for file in self.file_list:
            print(f"\tFull path: {file.full_path}")
            print(f"\tPath: {file.file_path}")
            print(f"\tFile name: {file.file_name}")
            print(f"\tFile extension: {file.file_ext}")
            print(f"\tWidth (px): {file.width_px}")
            print(f"\tHeight (px): {file.height_px}")
            print(f"\tWidth (um): {file.width_SI}")
            print(f"\tHeight (um): {file.height_SI}")
            print(f"\tmpp: {file.mpp}")
            print(f"\tFrames: {file.frames}")
            print(f"\tTime_lag: {file.time_lag}")
            print(f"\tFPS: {file.fps}")
            print(f"\tFilter: {file.filter}")

    def get_trajectories(self):
        data = pd.DataFrame()
        for file in self.file_list:
            if file.file_ext in (".csv"):
                print(f"File extension: {file.file_ext}")
                file_data = file.from_csv()
                data = data.append(file_data)
            elif file.file_ext in (".tif", ".tiff"):
                print(f"File extension: {file.file_ext}")
                file_data = file.from_tif()
                data = data.append(file_data)
                # elif file.file_ext in (".avi", ".tif", ".tiff"):
                #     print(f"File extension: {file.file_ext}")
            else:
                print(f"Unsupported file format ('{file.file_ext}').")

        return data

    # def start_analysis(self):
    #     for video in self.videos:
    #         video.preview()
    #         tp.annotate(video.features, video.frames[0])

    #         # TODO: Add decision and config for batch locate
    #         video.analyze()

    #         if video.trajectories['particle'].nunique() > 0:
    #             video.refine()
    #             video.analyze_trajectories()
    #             video.get_MSD()

    #             self.get_full_MSD(video.msd)

    #             video.get_EMSD()

    #             video.get_Deff()
    #             video.msd = mpt_utils.rename_columns(video.msd)
    #             video.deff = mpt_utils.rename_columns(video.deff)

    #             # Individual Particle Analysis report ------
    #             mpt_utils.export_individual_particle_analysis(video,
    #                                                           self.out_path)

    #             # Transport Mode Characterization report ----
    #             mpt_utils.export_transport_mode(video, self.out_path)

    # def get_full_MSD(self, new_msd):
    #     self.msd = pd.concat([self.msd, new_msd],
    #                          axis=1,
    #                          ignore_index=True,
    #                          sort=False)

    # def end(self) -> None:
    # print(self.analysis)
    # del self.analysis
