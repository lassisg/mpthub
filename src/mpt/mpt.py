import os
import tkinter as tk
from tkinter import filedialog
import wx
import pandas as pd
import numpy as np


class Report:
    def __init__(self) -> None:
        self.full_path = None
        self.folder_path = None
        self.file_name = None
        self.extension = None
        self.raw_data = pd.DataFrame()
        self.total_trajectories = 0
        self.valid_trajectories = 0
        self.valid_trajectories_number = []
        self.valid_trajectories_list = []
        self.msd = pd.DataFrame()
        self.deff = pd.DataFrame()

    def load_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.full_path)
        # data = pd.read_csv(self.full_path,
        #                    skiprows=1,
        #                    usecols=[0, 1, 2, 3],
        #                    names=['Trajectory', 'Frame', 'x', 'y'])
        data = self.clean_data(data)

        return data

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        if all([item in data.columns for item in ['Trajectory', 'Frame', 'x', 'y']]):
            return data
        else:
            return pd.DataFrame()

    def count_trajectories(self) -> None:
        if not self.raw_data.empty:
            self.total_trajectories = len(self.raw_data.iloc[:, :1].
                                          groupby('Trajectory').nunique())

    def filter_trajectories(self, filter: int) -> None:
        if not self.raw_data.empty and filter > 0:
            grouped_trajectories = self.raw_data.groupby(
                'Trajectory').filter(lambda x: len(x['Trajectory']) > filter)

            self.valid_trajectories_number = list(
                grouped_trajectories.iloc[:, :1].
                groupby('Trajectory').nunique().index)

            for trajectory in self.valid_trajectories_number:
                self.valid_trajectories_list.append(
                    grouped_trajectories.
                    loc[grouped_trajectories['Trajectory'] == trajectory].
                    reset_index(drop=True))

            self.valid_trajectories = len(self.valid_trajectories_number)

    def summarize_trajectories(self) -> None:
        traj_number = self.valid_trajectories_number
        traj_data = self.valid_trajectories_list
        for traj_nr, trajectory in zip(traj_number, traj_data):
            print(
                f"Trajectory {traj_nr} lenght: {len(trajectory.loc[trajectory['Trajectory'] == traj_nr])}")


class MPT:
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.out_path = None        # TODO: Ask user
        self.report_list = []
        self.filter = 0             # TODO: Add config
        self.total_frames = 0       # TODO: Add config
        self.fps = 0                # TODO: Add config
        self.msd = pd.DataFrame()
        self.deff = pd.DataFrame()
        self.trajectories_list = []

    def load_config(self, config: str) -> int:
        if config == "filter":
            return 590
        elif config == "frames":
            return 606
        elif config == "fps":
            return 30
        else:
            return 0

    def add_report(self) -> None:
        app = wx.App()

        with wx.FileDialog(None, "Open ImageJ Full report file(s)",
                           wildcard="ImageJ full report files (*.csv)|*.csv",
                           style=wx.FD_OPEN | wx.FD_MULTIPLE) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                print("No file selected...")
                return None  # the user changed their mind

            file_list = fileDialog.GetPaths()

            self.filter = self.load_config('filter')

            for file in file_list:
                new_report = Report()

                new_report.full_path = file
                new_report.folder_path = os.path.dirname(file)
                new_report.file_name, new_report.extension = os.path.splitext(
                    os.path.basename(file))
                new_report.raw_data = new_report.load_data()

                self.report_list.append(new_report)

                del new_report

    def analyze(self) -> None:
        for report in self.report_list:
            if report.raw_data.empty:
                print(f"Can't read file {report.file_name}. Wrong format?")
                continue

            print(f"Analyzing report file: '{report.file_name}'")

            report.count_trajectories()
            print(f"Total trajectories: {report.total_trajectories}")

            report.filter_trajectories(self.filter)
            print(f"Valid trajectories: {report.valid_trajectories}")

            # report.summarize_trajectories()
            self.trajectories_list.extend(report.valid_trajectories_list)

        print("Full trajectory list compiled. Initializing calculations...")
        # # ----------------------------------------------------------
        # time_step = 1 / self.fps
        # max_time = 606 / self.fps
        # tau = np.linspace(time_step, max_time, self.total_frames)

        # trajectories = []
        # msd = pd.DataFrame()

        # for j, trace in enumerate(traj_list):
        #     frames = len(trace)
        #     t = tau[:frames]

        #     xy = trace.values

        #     trajectory = pd.DataFrame({"t": t, "x": xy[:, -2], "y": xy[:, -1]})

        #     # Compute MSD
        #     shifts = trajectory["t"].index.values + 1
        #     msdp = np.zeros(shifts.size)
        #     for k, shift in enumerate(shifts):
        #         diffs_x = trajectory['x'] - trajectory['x'].shift(-shift)
        #         diffs_y = trajectory['y'] - trajectory['y'].shift(-shift)
        #         square_sum = np.square(diffs_x) + np.square(diffs_y)
        #         msdp[k] = square_sum.mean()

        #     msdm = msdp * (1 / 3.2 ** 2)
        #     msdm = msdm[:590]
        #     msd[j] = msdm

        #     trajectories.append(msd)
        # # ----------------------------------------------------------
        # tau = tau[:590]

        # msd.insert(0, "tau", tau, True)
        # msd = msd[msd[msd.columns[0]] < 10]

        # # deff = calc_deff(msd.copy())
        # msd_log = np.log10(msd)
        # msd_log['mean'] = msd_log.iloc[:, 1:].mean(axis=1)

        # msd['mean'] = msd.iloc[:, 1:].mean(axis=1)
        # # deff["mean"] = deff.iloc[:, 1:].mean(axis=1)

        # # msd = rename_columns(msd, "MSD")
        # # deff = rename_columns(deff, "Deff")
        # msd_log.to_csv(f"_Series00{i+1}.csv")
        # print("-----------\n")
