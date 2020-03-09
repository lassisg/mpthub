import os
import wx
import pandas as pd
from pandas import ExcelWriter as xls
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


class Result:
    def __init__(self) -> None:
        print("Result instance created...")

    def get_slopes(dataIn: pd.DataFrame) -> pd.Series:
        return pd.Series([np.polyfit(dataIn[dataIn.columns[0]],
                                     np.asarray(dataIn[column]), 1)[0]
                          for column in dataIn.columns[1:-1]])

    def get_diffusivity_ranges(CFG_PATH):
        return pd.read_json(os.path.join(CFG_PATH, "cfg-diffusivity.json"))

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

    def export_individual_particle_analysis(data, path):
        print("Exporting 'Individual Particle Analysis' report...")
        file_name = os.path.join(path,
                                 data.name + " - Individual Particle Analysis.xlsx")

        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        data.msd.to_excel(writer, sheet_name='Data',
                          startrow=1)
        data.deff.to_excel(writer, sheet_name='Data',
                           startrow=len(data.msd)+4)
        workbook = writer.book

        sheet_format = workbook.add_format({'align': 'center',
                                            'valign': 'vcenter'})
        header_format = workbook.add_format({'align': 'center',
                                             'valign': 'vcenter',
                                             'bold': 1})

        data_sheet = writer.sheets['Data']
        data_sheet.set_row(1, 21, header_format)
        data_sheet.set_row(len(data.msd)+4, 21, header_format)
        # data_sheet.set_column(0, 0, 15, sheet_format)
        # data_sheet.set_column(1, len(current_vid.msd.columns), 12, sheet_format)
        data_sheet.set_column(0, len(data.msd.columns), 15, sheet_format)

        data_sheet = writer.sheets['Data']

        msd_title = f'{data.msd.name} Data'
        data_sheet.merge_range(0, 0,
                               0, len(data.msd.columns),
                               msd_title, header_format)

        deff_title = f'{data.deff.name} Data'
        data_sheet.merge_range(len(data.msd)+3,
                               0,
                               len(data.msd) + 3,
                               len(data.msd.columns),
                               deff_title, header_format)

        make_chart(workbook, data.msd, 1)
        make_chart(workbook, data.deff, len(data.msd)+4)

        workbook.close()
        writer.save()

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

    def export_transport_mode(data, path):
        print("Export transport mode sheet")
        data.log_msd = np.log10(data.msd.reset_index())
        data.log_msd.name = data.msd.name

        columns = data.msd.shape[1]

        file_name = os.path.join(path,
                                 data.name + " - Transport Mode Characterization.xlsx")

        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')

        data.log_msd.to_excel(writer, sheet_name='Data',
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
        data_sheet.set_row(len(data.msd)+4, 21, header_format)
        data_sheet.set_column(0, columns, 15, sheet_format)

        data_sheet = writer.sheets['Data']

        msd_title = f'{data.log_msd.name} Data'
        data_sheet.merge_range(0, 0,
                               0, columns,
                               msd_title, header_format)

        # Add guide series data
        slopeData = get_slopes(data.log_msd)
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

        make_chart_LOG(workbook, data.log_msd, 1)

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

        diff_ranges = get_diffusivity_ranges(data.config_path)

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


class MPT:
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self.out_path = None        # TODO: Ask user / Add config / =input path
        self.report_list = []
        self.filter = 0
        self.total_frames = 0
        self.fps = 0
        self.width_px = 0
        self.width_um = 0
        self.pixel_size = 0.0
        self.msd = pd.DataFrame()
        self.deff = pd.DataFrame()
        self.msd_log = pd.DataFrame()
        self.trajectories_list = []

    def load_config(self) -> None:
        # TODO: Load setting from file/DB
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

    def analyze(self) -> None:
        for report in self.report_list:
            if report.raw_data.empty:
                print(f"\nCan't read file {report.file_name}. Wrong format?")
                continue

            print(f"\nAnalyzing report file: '{report.file_name}'")

            report.count_trajectories()
            print(f"Total trajectories: {report.total_trajectories}")

            report.filter_trajectories(self.filter)
            print(f"Valid trajectories: {report.valid_trajectories}")

            # report.summarize_trajectories()
            self.trajectories_list.extend(report.valid_trajectories_list)

        print("\nFull trajectory list compiled. Initializing calculations...")

        self.compute_msd()

    def export(self) -> None:
        print("\nExporting reports...")
        result = Result()
