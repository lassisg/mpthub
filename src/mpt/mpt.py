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
            return data.loc[:, ['Trajectory', 'Frame', 'x', 'y']]
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
        self.out_path = None        # TODO: Ask user / Add config / =input path
        self.report_list = []
        self.filter = 0             # TODO: Add config
        self.total_frames = 0       # TODO: Add config
        self.fps = 0                # TODO: Add config
        self.width_px = 0           # TODO: Add config
        self.width_um = 0           # TODO: Add config
        self.pixel_size = 0.0       # TODO: Calculate from config
        self.msd = pd.DataFrame()
        self.deff = pd.DataFrame()
        self.msd_log = pd.DataFrame()
        self.trajectories_list = []

    def load_config(self) -> None:
        self.filter = 590
        self.fps = 30
        self.total_frames = 606
        self.width_px = 512
        self.width_um = 160
        self.pixel_size = self.width_px / self.width_um

    def add_report(self) -> None:
        app = wx.App()

        with wx.FileDialog(None, "Open ImageJ Full report file(s)",
                           wildcard="ImageJ full report files (*.csv)|*.csv",
                           style=wx.FD_OPEN | wx.FD_MULTIPLE) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                print("No file selected...")
                return None  # the user changed their mind

            file_list = fileDialog.GetPaths()

            self.load_config()

            for file in file_list:
                new_report = Report()

                new_report.full_path = file
                new_report.folder_path = os.path.dirname(file)
                new_report.file_name, new_report.extension = os.path.splitext(
                    os.path.basename(file))
                new_report.raw_data = new_report.load_data()

                self.report_list.append(new_report)

                del new_report

    def rename_columns(self, name: str) -> pd.DataFrame:

        if name == self.msd.name:
            data = self.msd
        elif name == self.msd_log.name:
            data = self.msd
        else:
            data = self.deff

        name = data.name.split('-')[0]
        unit = f"{chr(956)}m{chr(178)}"

        columns_names = pd.Series(range(1, len(data.columns)+1))-1
        columns_names = [f'{name} {x+1} ({unit})' for x in columns_names]
        columns_names[len(columns_names) - 1] = f'<{name}> ({unit})'

        data.columns = columns_names

        return data

    def compute_msd(self) -> None:
        time_step = 1 / self.fps
        max_time = self.total_frames / self.fps
        tau = np.linspace(time_step, max_time, self.total_frames)

        for i, trajectory in enumerate(self.trajectories_list):
            frames = len(trajectory)
            t = tau[:frames]

            xy = trajectory.values

            position = pd.DataFrame({"t": t, "x": xy[:, -2], "y": xy[:, -1]})

            # Compute MSD
            shifts = position["t"].index.values + 1
            msdp = np.zeros(shifts.size)
            for j, shift in enumerate(shifts):
                diffs_x = position['x'] - position['x'].shift(-shift)
                diffs_y = position['y'] - position['y'].shift(-shift)
                square_sum = np.square(diffs_x) + np.square(diffs_y)
                msdp[j] = square_sum.mean()

            msdm = msdp * (1 / (self.pixel_size ** 2))
            msdm = msdm[:self.filter]
            self.msd[i] = msdm

        tau = tau[:self.filter]

        self.msd.insert(0, "tau", tau, True)
        self.msd = self.msd[self.msd[self.msd.columns[0]] < 10]

        self.msd.name = "MSD"
        self.msd.set_index('tau', inplace=True)
        self.msd.index.name = f'Timescale ({chr(120591)}) (s)'
        self.msd['mean'] = self.msd.iloc[:, 1:].mean(axis=1)

        self.msd_log = np.log10(self.msd.iloc[:, :-1])
        self.msd_log.name = "MSD-LOG"
        self.msd_log['mean'] = self.msd_log.iloc[:, 1:].mean(axis=1)

        self.deff = self.msd.iloc[:, :-1].div((4*self.msd.index), axis=0)
        self.deff.name = "Deff"
        self.deff["mean"] = self.deff.iloc[:, :].mean(axis=1)

        self.msd = self.rename_columns("MSD")
        self.msd_log = self.rename_columns("MSD-LOG")
        self.deff = self.rename_columns("Deff")
        print("-----------\n")

    def analyze(self) -> None:
        for report in self.report_list:
            if report.raw_data.empty:
                print(f"Can't read file {report.file_name}. Wrong format?")
                continue

            print(f"\nAnalyzing report file: '{report.file_name}'")

            report.count_trajectories()
            print(f"Total trajectories: {report.total_trajectories}")

            report.filter_trajectories(self.filter)
            print(f"Valid trajectories: {report.valid_trajectories}")

            # report.summarize_trajectories()
            self.trajectories_list.extend(report.valid_trajectories_list)

        print("Full trajectory list compiled. Initializing calculations...")

        self.compute_msd()
