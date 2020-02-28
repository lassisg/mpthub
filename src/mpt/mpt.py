# from mpt.analysis import Analysis
from mpt.mpt_file import MPT_File
import mpt.utils as mpt_utils
import tkinter as tk
from tkinter import filedialog
import os
import trackpy as tp
import pandas as pd
import math
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('WXAgg')


class MPT():
    def __init__(self, config_path: str) -> None:
        super().__init__()
        self.config_path = config_path
        self.out_path = os.path.join(self.config_path, 'export')
        self.file_list = []
        self.trajectories = pd.DataFrame()
        self.filter = None
        self.msd = pd.DataFrame()
        self.deff = pd.DataFrame()
        self.emsd = pd.Series()

    def add_file(self) -> None:
        root = tk.Tk()
        root.withdraw()

        file_list = filedialog.askopenfilenames()

        if not file_list:
            print("No file selected...")
            return None

        for file in file_list:
            new_item = MPT_File()

            new_item.config_path = self.config_path
            new_item.full_path = file
            new_item.file_path = os.path.dirname(file)
            new_item.file_name, new_item.file_ext = os.path.splitext(
                os.path.basename(file))

            if new_item.file_ext in (".tif", ".tiff"):
                new_item.get_tif_metadata()

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
            elif file.file_ext in (".avi"):
                print(f"File extension: {file.file_ext}")
                file_data = file.from_avi()
                data = data.append(file_data)
            else:
                print(f"Unsupported file format ('{file.file_ext}').")

        self.trajectories = data

    def filter_trajectories(self) -> None:
        # ============================ Filter spurious trajectories
        print("Filtering trajectories...")
        previous = self.trajectories['particle'].nunique()

        self.trajectories = tp.filter_stubs(
            self.trajectories, self.file_list[0].filter)

        # Compare the number of particles in the unfiltered and filtered data.
        print(f"Before: {previous}")
        print(f"After: \t{self.trajectories['particle'].nunique()}")

    def refine_trajectories(self) -> None:
        # # Convenience function -- just plots size vs. mass
        # tp.mass_size(self.trajectories.groupby('particle').mean())

        # # mass: brightness of the particle
        # # size: diameter of the particle
        # # ecc: eccentricity of the particle (0 = circular)
        # t2 = self.trajectories[(
        #     (self.trajectories['mass'] > self.m_mass) &
        #     (self.trajectories['size'] < self.m_size) &
        #     (self.trajectories['ecc'] < self.m_ecc))]

        # tp.annotate(t2[t2['frame'] == 0], self.frames[0])

        # ax = tp.plot_traj(t2)
        # plt.show()

        # ============================== Remove overall drift
        print("Removing drift...")
        drift = tp.compute_drift(self.trajectories)
        # drift.plot()
        # plt.show()

        self.trajectories = tp.subtract_drift(self.trajectories.copy(), drift)
        # ax = tp.plot_traj(self.trajectories)
        # plt.show()

    def analyze_trajectories(self) -> None:
        # ============================== Analyze trajectories
        print("Analyzing trajectories...")
        fps = self.file_list[0].fps
        mpp = self.file_list[0].mpp
        mlt = math.ceil(fps*10)  # Time to use (10s, 1s, 0.1s)

        # ============================== Mean Squared Displacement
        self.msd = tp.imsd(self.trajectories, mpp, fps, mlt)

        # fig, ax = plt.subplots()
        # # black lines, semitransparent
        # ax.plot(self.msd.index, self.msd, 'k-', alpha=0.1)
        # ax.set(ylabel=r'MSD [$\mu$m$^2$]', xlabel='Timescale ($\\tau$) [$s$]')
        # ax.set_xscale('log')
        # ax.set_yscale('log')

        self.msd.name = "MSD"
        self.msd.index.name = f'Timescale ({chr(120591)}) (s)'

        # ============================== Ensemble Mean Squared Displacement
        # Best option ?
        self.emsd = tp.emsd(self.trajectories, mpp, fps, mlt)
        self.msd['mean2'] = self.emsd.values

        # fig, ax = plt.subplots()
        # ax.plot(self.msd['mean'].index, self.msd['mean'], 'o')
        # ax.set_xscale('log')
        # ax.set_yscale('log')
        # ax.set(ylabel=f'MSD {chr(956)}m{chr(178)}',
        #        xlabel='Timescale ($\\tau$) [$s$]')

        # plt.figure()
        # plt.title('Ensemble Data - <MSD> vs. Time Scale')
        # plt.ylabel(f'MSD {chr(956)}m{chr(178)}')
        # plt.xlabel('Timescale ($\\tau$) [$s$]')
        # tp.utils.fit_powerlaw(self.msd['mean'])
        # print(f"n: {n}, A: {A}")

        # ============================== Diffusivity coeficient
        self.deff = self.msd.div((4*self.msd.index), axis=0)
        self.deff.name = "Deff"

        self.msd = mpt_utils.rename_columns(self.msd)
        self.deff = mpt_utils.rename_columns(self.deff)

    def export_reports(self):
        # Individual Particle Analysis report ------
        mpt_utils.export_individual_particle_analysis(self, self.out_path)

        # Transport Mode Characterization report ----
        mpt_utils.export_transport_mode(self, self.out_path)
