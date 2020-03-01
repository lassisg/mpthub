# from mpt.analysis import Analysis
# from mpt.mpt_partial import MPT_Partial
import mpt.utils as mpt_utils
# import tkinter as tk
# from tkinter import filedialog
import os
import skvideo.io
import exifread
# import skvideo.datasets
# import skvideo.utils
import pims
import trackpy as tp
import numpy as np
import pandas as pd
from pandas import ExcelWriter as xls
import math
from math import ceil
import wx
import matplotlib
from matplotlib import pyplot as plt
matplotlib.use('WXAgg')


class MPT_Full():
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


class MPT_Partial():
    def __init__(self) -> None:
        self.config_path = None
        self.full_path = None
        self.file_path = None
        self.file_name = None
        self.file_ext = None
        # Ask User in config
        self.frames = 606
        self.width_px = 512
        self.height_px = 512
        self.width_SI = 160
        self.height_SI = 160
        self.fps = 30
        self.f_size = 11
        # Calculate from user input
        self.filter = ceil(self.frames * .975)
        self.mpp = self.width_SI/self.width_px
        self.time_lag = 1 / self.fps

        self.trajectories = pd.DataFrame()
        self.msd = pd.DataFrame()
        self.deff = pd.DataFrame()
        self.emsd = pd.Series()

        # self.m_mass = None
        # self.m_size = None
        # self.m_ecc = None
        # self.mlt = 0.0
        # self.features = pd.DataFrame()  # particles
        # self.trajectories = pd.DataFrame()
        # self.msd = pd.DataFrame()
        # self.deff = pd.DataFrame()

    def from_txt(self) -> pd.DataFrame:

        f = open(self.full_path)
        f_list = list(f)
        first_trajectory_row = f_list.index('%% Trajectory 1\n')
        f.close()

        rows_to_skip = first_trajectory_row + 1

        data = pd.read_csv(
            self.full_path,
            skiprows=rows_to_skip,
            delim_whitespace=True,
            usecols=[0, 1, 2],
            names=["frame", "x", "y"],
            # decimal=",",
        )
        return data

    def from_csv(self) -> pd.DataFrame:
        data = pd.read_csv(
            self.full_path,
            skiprows=1,
            usecols=[0, 1, 2, 3],
            names=["particle", "frame", "x", "y"],
            # decimal=",",
        )
        return data

    def from_tif(self) -> pd.DataFrame:
        # ============================== Opening file
        frames = pims.open(self.full_path)

        print("Locating particles...")
        features = tp.locate(frames[0], self.f_size)
        # tp.annotate(f, self.frames[0])

        # ============================== Refine parameters
        print("Refining parameters...")
        self.m_mass = math.ceil(features.mass.mean())
        self.m_size = math.floor(features.size.mean())
        self.m_ecc = features.ecc.mean()

        # ============================== Relocate features according to mass
        print(f"Relocating particles...\n")
        features = tp.locate(frames[0], self.f_size, minmass=self.m_mass)

        # ============================== Subpixel accuracy
        # TODO: Clear axis after this plot
        tp.subpx_bias(features)
        # plt.imshow(frames[0])

        tp.annotate(features, frames[0])

        # ============================ Locate features in all frames
        print(f"\nLocating particles in all frames...")
        tp.quiet()
        features = tp.batch(frames[:], self.f_size, minmass=self.m_mass)
        # processes="auto")

        # ============================ Link features into particle trajectories
        print("Linking particles into trajectories...")
        data = tp.link(features, self.f_size, memory=0)

        return data

    def from_avi(self) -> pd.DataFrame:
        # ============================== Opening file
        frames = pims.open(self.full_path)

        print("Locating particles...")
        features = tp.locate(frames[0], self.f_size)
        # tp.annotate(f, self.frames[0])

        # ============================== Refine parameters
        print("Refining parameters...")
        self.m_mass = math.ceil(features.mass.mean())
        self.m_size = math.floor(features.size.mean())
        self.m_ecc = features.ecc.mean()

        # ============================== Relocate features according to mass
        print(f"Relocating particles...\n")
        features = tp.locate(frames[0], self.f_size, minmass=self.m_mass)

        # ============================== Subpixel accuracy
        # TODO: Clear axis after this plot
        tp.subpx_bias(features)
        # plt.imshow(frames[0])

        tp.annotate(features, frames[0])

        # ============================ Locate features in all frames
        print(f"\nLocating particles in all frames...")
        features = tp.batch(frames[:],
                            self.f_size,
                            minmass=self.m_mass,
                            processes="auto")

        # ============================ Link features into particle trajectories
        print("Linking particles into trajectories...")
        data = tp.link(features, self.f_size, memory=0)

        return data

    # TODO: Find a way to run without the need to create tif files
    def get_lif_metadata(self) -> None:
        lif_file = LifFile(self.full_path)

        for i, image in enumerate(lif_file.get_iter_image()):
            new_series = Series()
            new_series.index = i
            new_series.filename = image.filename
            new_series.name = image.name
            new_series.frames = image.nt
            new_series.width_px = image.dims[0]
            new_series.height_px = image.dims[1]
            new_series.mpp = image.scale[0]
            new_series.width_SI = math.floor(
                new_series.width_px / image.scale[0])
            new_series.height_SI = math.floor(
                new_series.height_px / image.scale[1])
            new_series.fps = image.scale[-1]
            new_series.time_lag = 1 / new_series.fps

        del lif_file

    def get_tif_metadata(self) -> None:
        # print("tif file selected")
        tif_file = open(self.full_path, 'rb')

        tags = exifread.process_file(tif_file)

        frame_tag = str(tags['Image PageNumber'])
        frame_tag = frame_tag.replace(']', '')
        frame_tag = frame_tag.split(',')

        image_x_px, image_x_cm = str(tags['Image XResolution']).split('/')
        # image_y_px, image_y_cm = str(tags['Image YResolution']).split('/')

        # for tag in tags.keys():
        #     print(f"tag: {tag}, value: {tags[tag]}")

        self.frames = int(frame_tag[-1])
        self.filter = ceil(self.frames * .975)
        self.width_px = int(str(tags['Image ImageWidth']))
        self.height_px = int(str(tags['Image ImageLength']))
        self.mpp = (int(image_x_cm) * 10000)/int(image_x_px)
        self.width_SI = math.floor(self.mpp * self.width_px)
        self.height_SI = math.floor(self.mpp * self.height_px)
        self.time_lag = 1 / self.fps

        del tif_file

    def filter_trajectories(self) -> None:
        # ============================ Filter spurious trajectories
        print("Filtering trajectories...")
        previous = self.trajectories['particle'].nunique()

        self.trajectories = tp.filter_stubs(
            self.trajectories, self.filter)

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


class MPT_Utils():
    @staticmethod
    def rename_columns(data: pd.DataFrame) -> pd.DataFrame:
        columns_names = pd.Series(range(1, len(data.columns)+1))-1
        columns_names = [
            f'{data.name} {x+1} ({chr(956)}m{chr(178)})' for x in columns_names]
        columns_names[len(columns_names) -
                      1] = f'<{data.name}> ({chr(956)}m{chr(178)})'
        data.columns = columns_names

        return data

    @staticmethod
    def get_slopes(dataIn: pd.DataFrame):
        return pd.Series([np.polyfit(dataIn[dataIn.columns[0]],
                                     np.asarray(dataIn[column]), 1)[0]
                          for column in dataIn.columns[1:-1]])

    @staticmethod
    def make_chart(workbook: xls.book, data: pd.DataFrame, start_row: int):
        #       (workbook: xls.book, data: df, data_name: str, startrow: int):

        # Create a chart object.
        chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})
        mean_chart = workbook.add_chart(
            {'type': 'scatter', 'subtype': 'smooth'})

        # Configure the series of the chart from the dataframe data.
        columns = data.shape[1]
        for i in range(1, columns + 1):
            chart.add_series({
                'name': ['Data', start_row, i],
                'categories': ['Data', start_row + 1, 0, start_row + len(data), 0],
                'values': ['Data', start_row + 1, i, start_row + len(data), i],
                'trendline': False,
            })

        mean_chart.add_series({
            'name': ['Data', start_row, columns],
            'categories': ['Data', start_row+1, 0, start_row+len(data), 0],
            'values': ['Data', start_row+1, columns, start_row+len(data), columns],
        })

        # Add a chart title, style and some axis labels.
        chart.set_x_axis({'name': f'Time Scale ({chr(120591)}) (s)'})
        chart.set_y_axis({'name': f'{data.name} ({chr(956)}m²)'})
        chart.set_legend({'none': True})
        chart.set_style(1)

        # Add a chart title, style and some axis labels.
        mean_chart.set_title(
            {'name': f'Ensemble Data - <{data.name}> vs. Time Scale'})
        mean_chart.set_x_axis({'name': f'Time Scale ({chr(120591)}) (s)'})
        mean_chart.set_y_axis({'name': f'{data.name} ({chr(956)}m²)'})
        mean_chart.set_legend({'none': True})
        mean_chart.set_style(1)

        # Insert the chart into the worksheet.
        mean_time_chart = workbook.add_chartsheet(f'<{data.name}> vs Time')
        mean_time_chart.set_chart(mean_chart)

        # Insert the chart into the worksheet.
        time_chart = workbook.add_chartsheet(f'{data.name} vs Time')
        time_chart.set_chart(chart)

    @staticmethod
    def make_chart_LOG(workbook: xls.book, data: pd.DataFrame, start_row: int):
        """Creates a log-log plot from given data.

        Arguments:
            workbook {ExcelWriter.book} -- Excel file to add the chart
            data {Dataframe} -- Data do populate the chart
            data_name {str} -- Title of the data
            startrow {int} -- Starting row for data entry
        """

        # Create a chart object.
        chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})

        # Configure the series of the chart from the dataframe data.
        trendLine = False
        if data.name in "MSD":
            trendLine = {
                'type': 'linear',
                'display_equation': True,
                'line': {'none': True},
                'data_labels': {'position': True}
            }

        columns = data.shape[1]
        for i in range(1, columns):
            chart.add_series({
                'name': ['Data', start_row, i],
                'categories': ['Data', start_row + 1, 0, start_row + len(data), 0],
                'values': ['Data', start_row + 1, i, start_row + len(data), i],
                'trendline': False,
            })

        # i = 1
        # for column in data.columns[0:-2]:
        #     chart.add_series({
        #         'name': ['Data', startrow, i],
        #         'categories': ['Data', startrow+1, 0, startrow+len(data), 0],
        #         'values': ['Data', startrow+1, i, startrow+len(data), i],
        #         'trendline': trendLine,
        #     })
        #     i += 1

        # Add guides series
        chart.add_series({
            'name': ['Data', 3, columns+2],
            'categories': ['Data', 4, columns+1, 5, columns+1],
            'values': ['Data', 4, columns+2, 5, columns+2],
            'line': {
                'color': 'black',
                'width': 1.25,
                'dash_type': 'square_dot'},
            # 'trendline': trendLine,
        })
        chart.add_series({
            'name': ['Data', 3, columns+3],
            'categories': ['Data', 4, columns+1, 5, columns+1],
            'values': ['Data', 4, columns+3, 5, columns+3],
            'line': {
                'color': 'red',
                'width': 1.25,
                'dash_type': 'square_dot'},
            # 'trendline': trendLine,
        })
        chart.add_series({
            'name': ['Data', 3, columns+4],
            'categories': ['Data', 4, columns+1, 5, columns+1],
            'values': ['Data', 4, columns+4, 5, columns+4],
            'line': {
                'color': 'black',
                'width': 1.25,
                'dash_type': 'square_dot'},
            # 'trendline': trendLine,
        })
        # ----------------

        # Add a chart title, style and some axis labels.
        chart.set_x_axis({'name': f'Time Scale ({chr(120591)}) (s)'})
        chart.set_y_axis({'name': f'{data.name} ({chr(956)}m²)'})
        chart.set_legend({'none': True})
        chart.set_style(1)

        # Insert the chart into the worksheet.
        time_chart = workbook.add_chartsheet(f'{data.name} vs Time')
        time_chart.set_chart(chart)

    @staticmethod
    def get_diffusivity_ranges(CFG_PATH):
        return pd.read_json(os.path.join(CFG_PATH, "cfg-diffusivity.json"))

    @staticmethod
    def export_individual_particle_analysis(current_vid, path):
        print("Exporting 'Individual Particle Analysis' report...")
        file_name = os.path.join(path,
                                 current_vid.name + " - Individual Particle Analysis.xlsx")

        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        current_vid.msd.to_excel(writer, sheet_name='Data',
                                 startrow=1)
        current_vid.deff.to_excel(writer, sheet_name='Data',
                                  startrow=len(current_vid.msd)+4)
        workbook = writer.book

        sheet_format = workbook.add_format({'align': 'center',
                                            'valign': 'vcenter'})
        header_format = workbook.add_format({'align': 'center',
                                             'valign': 'vcenter',
                                             'bold': 1})

        data_sheet = writer.sheets['Data']
        data_sheet.set_row(1, 21, header_format)
        data_sheet.set_row(len(current_vid.msd)+4, 21, header_format)
        # data_sheet.set_column(0, 0, 15, sheet_format)
        # data_sheet.set_column(1, len(current_vid.msd.columns), 12, sheet_format)
        data_sheet.set_column(
            0, len(current_vid.msd.columns), 15, sheet_format)

        data_sheet = writer.sheets['Data']

        msd_title = f'{current_vid.msd.name} Data'
        data_sheet.merge_range(0, 0,
                               0, len(current_vid.msd.columns),
                               msd_title, header_format)

        deff_title = f'{current_vid.deff.name} Data'
        data_sheet.merge_range(len(current_vid.msd)+3,
                               0,
                               len(current_vid.msd) + 3,
                               len(current_vid.msd.columns),
                               deff_title, header_format)

        make_chart(workbook, current_vid.msd, 1)
        make_chart(workbook, current_vid.deff, len(current_vid.msd)+4)

        workbook.close()
        writer.save()

    @staticmethod
    def export_transport_mode(current_vid, path):
        print("Export transport mode sheet")
        current_vid.log_msd = np.log10(current_vid.msd.reset_index())
        current_vid.log_msd.name = current_vid.msd.name

        columns = current_vid.msd.shape[1]

        file_name = os.path.join(path,
                                 current_vid.name + " - Transport Mode Characterization.xlsx")

        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        current_vid.log_msd.to_excel(writer, sheet_name='Data',
                                     startrow=1, index=False)
        workbook = writer.book

        sheet_format = workbook.add_format({'align': 'center',
                                            'valign': 'vcenter'})
        header_format = workbook.add_format({'align': 'center',
                                             'valign': 'vcenter',
                                             'bold': 1})
        num_format = workbook.add_format({'align': 'center',
                                          'valign': 'vcenter',
                                          'num_format': 1})

        data_sheet = writer.sheets['Data']
        data_sheet.set_row(1, 21, header_format)
        data_sheet.set_row(len(current_vid.msd)+4, 21, header_format)
        data_sheet.set_column(0, columns, 15, sheet_format)

        data_sheet = writer.sheets['Data']

        msd_title = f'{current_vid.log_msd.name} Data'
        data_sheet.merge_range(0, 0,
                               0, columns,
                               msd_title, header_format)

        # Add guide series data
        slopeData = get_slopes(current_vid.log_msd)
        b = slopeData[1].mean()

        data_sheet.merge_range(1, columns+2, 1, columns +
                               5, 'Guides', header_format)
        data_sheet.merge_range(2, columns+2, 3, columns+2, 'x', header_format)
        data_sheet.merge_range(2, columns+3, 2, columns+5, 'y', header_format)

        data_sheet.write(3, columns+3, 'm=0.9', header_format)
        data_sheet.write(3, columns+4, 'm=1', header_format)
        data_sheet.write(3, columns+5, 'm=1.1', header_format)

        col = columns + 2
        line = 4
        ref_cell = f'INDIRECT(ADDRESS({line+1}, {col+1}))'
        data_sheet.write(
            line, col, '=-2', num_format)
        data_sheet.write_formula(
            line, col+1, f'=0.9*{ref_cell}-0.2+{b}', num_format)
        data_sheet.write_formula(
            line, col+2, f'={ref_cell}+{b}', num_format)
        data_sheet.write_formula(
            line, col+3, f'=1.1*{ref_cell}+0.2+{b}', num_format)

        line += 1
        ref_cell = f'INDIRECT(ADDRESS({line+1},{col+1}))'
        data_sheet.write(
            line, col, '=2', num_format)
        data_sheet.write_formula(
            line, col+1, f'=0.9*{ref_cell}-0.2+{b}', num_format)
        data_sheet.write_formula(
            line, col+2, f'={ref_cell}+{b}', num_format)
        data_sheet.write_formula(
            line, col+3, f'=1.1*{ref_cell}+0.2+{b}', num_format)
        # ----------------------------

        make_chart_LOG(workbook, current_vid.log_msd, 1)

        slopeData.to_excel(writer, index=False, sheet_name='Characterization')

        sheet_format = workbook.add_format(
            {'align': 'center', 'valign': 'vcenter'})
        header_format = workbook.add_format({'align': 'center', 'bold': 1})

        data_sheet = writer.sheets['Characterization']
        data_sheet.set_column(0, 0, 4, header_format)
        data_sheet.set_column(0, 0, 12, sheet_format)
        data_sheet.set_column(3, 3, 18, sheet_format)
        data_sheet.set_column(4, 4, 12, sheet_format)
        data_sheet.set_column(5, 5, 7, sheet_format)

        data_sheet.write('A1', 'Slopes', header_format)
        data_sheet.write('D1', 'Transport Mode', header_format)
        data_sheet.write('E1', 'Slope', header_format)
        data_sheet.write('F1', 'Count', header_format)

        data_sheet.write('D2', 'Immobile')
        data_sheet.write('D3', 'Sub-diffusive')
        data_sheet.write('D4', 'Diffusive')
        data_sheet.write('D5', 'Active')

        diff_ranges = get_diffusivity_ranges(current_vid.config_path)

        immobile_low = float(diff_ranges.immobile.low)
        immobile_high = float('{0:.3g}'.format(
            diff_ranges.immobile.high-0.001))
        subdiffusive_low = float(
            '{0:.1g}'.format(diff_ranges.sub_diffusive.low))
        subdiffusive_high = float('{0:.3g}'.format(
            diff_ranges.sub_diffusive.high-0.001))
        diffusive_low = float('{0:.2g}'.format(diff_ranges.diffusive.low))
        diffusive_high = float('{0:.3g}'.format(
            diff_ranges.diffusive.high-0.001))
        active_low = float('{0:.2g}'.format(diff_ranges.active.low))

        data_sheet.write('E2', f'{str(immobile_low)}-{str(immobile_high)}')
        data_sheet.write(
            'E3', f'{str(subdiffusive_low)}-{str(subdiffusive_high)}')
        data_sheet.write('E4', f'{str(diffusive_low)}-{str(diffusive_high)}')
        data_sheet.write('E5', f'{str(active_low)}+')

        subdiffusive_txt = f'{str(subdiffusive_low).replace(".", ",")}'
        diffusive_txt = f'{str(diffusive_low).replace(".",",")}'
        active_txt = f'{str(active_low).replace(".",",")}'

        immobile_formula = f'=COUNTIF(A:A,"<{subdiffusive_txt}")'
        subdiffusive_formula = f'=COUNTIFS(A:A,">={subdiffusive_txt}",'
        subdiffusive_formula += f'A:A,"<{diffusive_txt}")'
        diffusive_formula = f'=COUNTIFS(A:A,">={diffusive_txt}",'
        diffusive_formula += f'A:A,"<{active_txt}")'
        active_formula = f'=COUNTIF(A:A,">={active_txt}")'

        data_sheet.write_formula('F2', immobile_formula)
        data_sheet.write_formula('F3', subdiffusive_formula)
        data_sheet.write_formula('F4', diffusive_formula)
        data_sheet.write_formula('F5', active_formula)

        # Statistical info
        summary_format = workbook.add_format(
            {'align': 'right', 'valign': 'vcenter'})
        data_sheet.write('D8', '<slope> = ', summary_format)
        data_sheet.write('D9', 'N = ', summary_format)
        data_sheet.write('D10', 'STD = ', summary_format)

        data_sheet.write_formula('E8', '=AVERAGE(A:A)')
        data_sheet.write_formula('E9', '=COUNT(A:A)')
        data_sheet.write_formula('E10', '=STDEV(A:A)')

        workbook.close()
        writer.save()
