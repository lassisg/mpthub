# from mpt.analysis import Analysis
from mpt.mpt_partial import MPT_Partial
import mpt.utils as mpt_utils
import tkinter as tk
from tkinter import filedialog
import os
import trackpy as tp
import pandas as pd
import math
import wx
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('WXAgg')


class MPT():
    def __init__(self, config_path: str) -> None:
        super().__init__()
        self.config_path = config_path
        self.out_path = os.path.join(self.config_path, 'export')
        self.file_list = []
        # self.trajectories = pd.DataFrame()
        self.filter = None
        self.msd = pd.DataFrame()
        self.deff = pd.DataFrame()
        self.emsd = pd.Series()

    def add_file(self) -> None:
        # root = tk.Tk()
        # root.withdraw()

        # file_list = filedialog.askopenfilenames()

        # if not file_list:
        #     print("No file selected...")
        #     return None

        # -----------------------------
        app = wx.App()
        # Create open file dialog
        allowed_files = "ImageJ trajectory report (*.csv)|*.csv"
        allowed_files += "|ImageJ full report (*.txt)|*.txt"
        allowed_files += "|TIF image file (*.tif)|*.tif"
        file_dialog = wx.FileDialog(None, "Open", "", "", allowed_files,
                                    wx.FD_OPEN | wx.FD_MULTIPLE)

        if file_dialog.ShowModal() == wx.ID_CANCEL:
            print("No file selected...")
            file_dialog.Destroy()
            return None

        file_list = file_dialog.GetPaths()
        file_dialog.Destroy()
        # -----------------------------

        for file in file_list:
            new_item = MPT_Partial()

            new_item.config_path = self.config_path
            new_item.full_path = file
            new_item.file_path = os.path.dirname(file)
            new_item.file_name, new_item.file_ext = os.path.splitext(
                os.path.basename(file))

            if new_item.file_ext in (".tif", ".tiff"):
                new_item.get_tif_metadata()
            elif new_item.file_ext in (".csv"):
                pass

            # elif new_item.file_ext in (".avi"):
            #     new_item.get_avi_metadata()

            self.file_list.append(new_item)

            del new_item

    def to_string(self) -> None:
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

    def get_trajectories(self) -> None:
        # data = pd.DataFrame()
        for file in self.file_list:
            if file.file_ext in (".csv"):
                print(f"File extension: {file.file_ext}")
                file.trajectories = file.from_csv()
                # data = data.append(file_data)
            elif file.file_ext in (".tif", ".tiff"):
                print(f"File extension: {file.file_ext}")
                file.trajectories = file.from_tif()
                # data = data.append(file_data)
            elif file.file_ext in (".avi"):
                print(f"File extension: {file.file_ext}")
                file.trajectories = file.from_avi()
                # data = data.append(file_data)
            else:
                print(f"Unsupported file format ('{file.file_ext}').")

        # self.trajectories = data

    def export_reports(self):
        # Individual Particle Analysis report ------
        mpt_utils.export_individual_particle_analysis(self, self.out_path)

        # Transport Mode Characterization report ----
        mpt_utils.export_transport_mode(self, self.out_path)
