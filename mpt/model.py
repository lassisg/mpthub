import mpt.database as db
import pandas as pd
from pandas import ExcelWriter as xls
import numpy as np
import os


class General():

    def __init__(self) -> None:
        # print("Initializing General app configuration object...")
        self.load_config()

    def load_config(self) -> None:
        """Loads configuration into a Series with data from database.
        """
        conn = db.connect()
        config_df = pd.read_sql_table("app_config", con=conn)
        self.config = config_df.iloc[0]

    def update(self, new_config: pd.Series) -> None:
        """Updates diffusivity ranges data on database.

        Arguments:
            new_config {pd.Series} -- New data to be updated in \
                diffusivity table.
        """
        conn = db.connect()
        new_config_df = new_config.to_frame(0).T
        new_config_df.to_sql('app_config', con=conn,
                             index=False, if_exists='replace')


class Diffusivity:

    def __init__(self) -> None:
        # print("Initializing Diffusivity configuration object...")
        self.load_config()

    def load_config(self) -> None:
        """Loads configuration into a DataFrame with data from database.
        """
        conn = db.connect()
        self.config = pd.read_sql_table("diffusivity", con=conn)

    def update(self, new_config: pd.DataFrame) -> None:
        """Updates diffusivity ranges data on database.

        Arguments:
            new_config {pd.DataFrame} -- New data to be updated in \
                diffusivity table.
        """
        conn = db.connect()
        new_config.to_sql('diffusivity', con=conn,
                          index=False, if_exists='replace')


class Analysis():

    def __init__(self) -> None:
        # print("Initializing Analysis configuration object...")
        self.summary = pd.DataFrame()
        self.load_config()

    def load_config(self) -> None:
        """Loads configuration into a Series with data from database.
        """
        conn = db.connect()
        config_df = pd.read_sql_table("analysis_config", con=conn)
        self.config = config_df.iloc[0]
        self.config['pixel_size'] = self.config.width_px / self.config.width_si

    def update(self, new_config: pd.Series) -> None:
        """Updates analysis_config ranges data on database.

        Arguments:
            new_config {pd.Series} -- New data to be updated in \
                analysis_config table.
        """
        conn = db.connect()
        new_config_df = new_config.to_frame(0).T
        new_config_df.to_sql('analysis_config', con=conn,
                             index=False, if_exists='replace')

    def load_reports(self, parent, file_list: list) -> None:
        """Loads '.csv' files into DB table 'trajectories' after filtering \
            by valid trajectories.

        Arguments:
            file_list {list} -- File path list to be imported.
        """
        self.trajectories = pd.DataFrame(
            columns=['file_name', 'Trajectory', 'Frame', 'x', 'y'])
        parent.statusBar.SetStatusText("Loading report(s)...")
        for file in file_list:
            if not self.summary.empty:
                masked_df = self.summary.full_path == file
                if masked_df.any():
                    continue

            full_data = pd.read_csv(file)
            file_name, _ = os.path.splitext(os.path.basename(file))
            if set(['Trajectory', 'Frame', 'x', 'y']).issubset(
                    full_data.columns):
                parent.statusBar.SetStatusText(f"File {file_name} ok!")
                raw_data = full_data.loc[:, ['Trajectory', 'Frame', 'x', 'y']]

                full_path = file

                parent.statusBar.SetStatusText(
                    f"Importing file {file_name}...")
                trajectories = len(
                    raw_data.iloc[:, :1].groupby('Trajectory').nunique())
                valid = self.get_valid_trajectories(
                    parent, file_name, raw_data)

                self.summary = self.summary.append({
                    'full_path': full_path, 'file_name': file_name,
                    'trajectories': trajectories, 'valid': valid},
                    ignore_index=True)
            else:
                parent.statusBar.SetStatusText(f"Wrong file format.")
                parent.statusBar.SetStatusText(
                    f"Aborting import of file: '{file_name}'")

        # if not self.trajectories.empty:
        self.add_trajectories(self.trajectories)

    def add_trajectories(self, data):
        conn = db.connect()
        data.to_sql('trajectories', con=conn,
                    index=False, if_exists='replace')

    def clear_summary(self):
        self.summary.drop(
            self.summary.index, inplace=True)

    def clear_trajectories(self) -> None:
        conn = db.connect()
        empty_data = pd.DataFrame(
            columns=['file_name', 'Trajectory', 'Frame', 'x', 'y'])
        empty_data.to_sql('trajectories', con=conn,
                          index=False, if_exists='replace')

    def get_valid_trajectories(self, parent,
                               file_name: str,
                               data_in: pd.DataFrame) -> int:
        parent.statusBar.SetStatusText(
            f"Filtering valid trajectories on {file_name}...")
        grouped_trajectories = data_in.groupby('Trajectory').filter(
            lambda x: len(x['Trajectory']) > self.config.min_frames)

        valid_trajectories = grouped_trajectories.iloc[:, :1].groupby(
            'Trajectory').nunique()

        valid_trajectories_data = data_in[data_in['Trajectory'].isin(
            valid_trajectories.iloc[:, 0].index.values)]
        valid_trajectories_data.insert(0, 'file_name', file_name)
        self.trajectories = self.trajectories.append(
            valid_trajectories_data, ignore_index=True)

        return len(valid_trajectories)

    def start(self, parent):
        parent.statusBar.SetStatusText(
            f"Computing MSD (mean squared displacement)...")

        self.msd = self.compute_msd(parent)
        self.msd_log = self.compute_msd_log(self.msd)

        parent.statusBar.SetStatusText(
            f"Computing Deff (diffusivity coefficient)...")
        self.deff = self.compute_deff(self.msd)

        parent.statusBar.SetStatusText(
            f"Adjusting data labels...")
        self.msd = self.rename_columns(self.msd)
        self.msd_log = self.rename_columns(self.msd_log)
        self.deff = self.rename_columns(self.deff)

    def compute_msd(self, parent) -> pd.DataFrame:
        """Computes the Mean-squared Displacement (MSD).
        It is mandatory to have configuration data previously loaded.

        Returns:
            pd.DataFrame -- Pandas DataFrame containing analysis MSD.
        """
        # TODO: Raise error if anything goes wrong
        time_step = 1 / self.config.fps
        max_time = self.config.total_frames / self.config.fps
        tau = np.linspace(time_step, max_time, int(self.config.total_frames))

        msd = pd.DataFrame()
        trajectories_group = self.trajectories.groupby(
            ['file_name', 'Trajectory'])

        i = 0
        for (file, trajectory), trajectory_data in trajectories_group:
            parent.statusBar.SetStatusText(
                f"Computing MSD for trajectory {trajectory} of file {file}...")

            frames = len(trajectory_data)
            t = tau[:frames]
            xy = trajectory_data.values

            position = pd.DataFrame({"t": t, "x": xy[:, -2], "y": xy[:, -1]})
            shifts = position["t"].index.values + 1
            msdp = self.compute_msdp(position, shifts)
            # for k, shift in enumerate(shifts):
            #     diffs_x = position['x'] - position['x'].shift(-shift)
            #     diffs_y = position['y'] - position['y'].shift(-shift)
            #     square_sum = np.square(diffs_x) + np.square(diffs_y)
            #     msdp[k] = square_sum.mean()

            msdm = msdp * (1 / (self.config.pixel_size ** 2))
            msdm = msdm[:int(self.config.min_frames)]
            msd[i] = msdm
            i += 1

        tau = tau[:int(self.config.min_frames)]

        msd.insert(0, "tau", tau, True)
        msd = msd[msd[msd.columns[0]] < 10]

        msd.name = "MSD"
        msd.set_index('tau', inplace=True)
        msd.index.name = f'Timescale ({chr(120591)}) (s)'
        msd['mean'] = msd.mean(axis=1)

        return msd

    def compute_msdp(self, position, shifts):
        msdp = np.zeros(shifts.size)
        for k, shift in enumerate(shifts):
            diffs_x = position['x'] - position['x'].shift(-shift)
            diffs_y = position['y'] - position['y'].shift(-shift)
            square_sum = np.square(diffs_x) + np.square(diffs_y)
            msdp[k] = square_sum.mean()

        return msdp

    def compute_msd_log(self, msd: pd.DataFrame) -> pd.DataFrame:
        """Computes the log version of Mean-squared Displacement.
        It is mandatory that the MSD is already computed.

        Arguments:
            msd {pd.DataFrame} -- Pandas DataFrame containing analysis MSD.

        Returns:
            pd.DataFrame -- Pandas DataFrame containing MSD values in \
                logarithm scale. Returns an empty Pandas DataFrame if \
                MSD DataFrame is empty.
        """
        if msd.empty:
            return pd.DataFrame()

        msd_log = np.log10(msd.reset_index().iloc[:, :-1])
        # msd_log.reset_index()
        msd_log.set_index(
            f'Timescale ({chr(120591)}) (s)', inplace=True)
        msd_log.name = "MSD-LOG"
        msd_log['mean'] = msd_log.mean(axis=1)

        return msd_log

    def compute_deff(self, msd: pd.DataFrame) -> pd.DataFrame:
        """Calculate Diffusivity efficiency coefficient (Deff).
        It is mandatory that the Mean-squared Displacement (MSD) \
            is already computed.

        Arguments:
            msd {pd.DataFrame} -- Pandas DataFrame containing analysis MSD.

        Returns:
            pd.DataFrame -- Pandas DataFrame containing Diffusivity \
                coefficients values. Returns an empty Pandas DataFrame \
                if MSD DataFrame is empty.
        """
        if self.msd.empty:
            return pd.DataFrame()

        deff = msd.iloc[:, :-1].div((4*msd.index), axis=0)
        deff.name = "Deff"
        deff["mean"] = deff.mean(axis=1)

        return deff

    def rename_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """Rename Pandas DataFrame columns to meaningfull names according \
            with the input's Pandas DataFrame name.

        Arguments:
            data {pd.DataFrame} -- Pandas DataFrame with columns in an \
                undesired naming.

        Returns:
            pd.DataFrame -- Input Pandas DataFrame with renamed \
                columns. No data changed.
        """
        header = data.name
        unit = f"{chr(956)}m{chr(178)}"

        columns_names = pd.Series(range(1, len(data.columns)+1))-1
        columns_names = [f'{header} {x+1} ({unit})' for x in columns_names]
        columns_names[len(columns_names) - 1] = f'<{header}> ({unit})'

        data.columns = columns_names

        return data

    def export(self, parent):
        """Call specific export functions.
        """
        report = Report()

        parent.statusBar.SetStatusText(
            f"Exporting 'Individual Particle Analysis' report...")
        report.export_individual_particle_analysis(
            parent.general.config.save_folder, self.msd, self.deff)

        parent.statusBar.SetStatusText(
            f"Exporting transport mode sheet...")
        report.export_transport_mode(
            parent.general.config.save_folder, self.msd_log)

        parent.statusBar.SetStatusText(
            f"Exporting Einstein-Stokes sheet...")
        report.export_einstein_stokes(
            parent.general.config.save_folder, self.msd_log)


class Report():

    def __init__(self) -> None:
        """Inform user that the result is being exported.
        """
        self.load_config()

    def load_config(self) -> None:
        """Loads configuration into a Series with data from database.
        """
        conn = db.connect()
        self.config = pd.read_sql_table("diffusivity", con=conn)
        self.config.rename(index={0: 'min', 1: 'max'}, inplace=True)

    def get_slopes(self, dataIn: pd.DataFrame) -> pd.Series:
        """Return the slope (alfa) from each trajectory's MSD.

        Arguments:
            dataIn {pd.DataFrame} -- DataFrame with all trajectories' MSD \
                in logarithm scale.

        Returns:
            pd.Series -- Series of slopes refering to each trajectory.
        """
        return pd.DataFrame([np.polyfit(dataIn.index.values,
                                        np.asarray(dataIn[column]), 1)
                             for column in dataIn.columns[:-1]])

    def make_chart(self, workbook: xls.book,
                   data: pd.DataFrame,
                   start_row: int) -> None:
        # TODO: Make function generic so it can be used for any chart
        """Create a chart for individual particle analysis.

        Arguments:
            workbook {xls.book} -- Excel spreadsheet object that will hod the \
                chart.
            data {pd.DataFrame} -- Data to be used for chart creation.
            start_row {int} -- Initial row to start the data series of the \
                chart.
        """

        # Create a chart object.
        chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})
        mean_chart = workbook.add_chart(
            {'type': 'scatter', 'subtype': 'smooth'})

        # Configure the series of the chart from the dataframe data.
        columns = data.shape[1]
        for i in range(1, columns + 1):
            chart.add_series({
                'name': ['Data', start_row, i],
                'categories': ['Data', start_row + 1, 0,
                               start_row + len(data), 0],
                'values': ['Data', start_row + 1, i,
                           start_row + len(data), i],
                'trendline': False,
            })

        mean_chart.add_series({
            'name': ['Data', start_row, columns],
            'categories': ['Data', start_row+1, 0,
                           start_row+len(data), 0],
            'values': ['Data', start_row+1, columns,
                       start_row+len(data), columns],
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

    def export_individual_particle_analysis(self,
                                            path: str,
                                            msd: pd.DataFrame,
                                            deff: pd.DataFrame):
        """Export 'Individual Particle Analysis' report file.

        Arguments:
            path {str} -- Path to the file.
            msd {pd.DataFrame} -- DataFrame containing MSD Data.
            deff {pd.DataFrame} -- DataFrame containing Deff data.
        """
        file_name = "Individual Particle Analysis"
        full_path = os.path.join(path, file_name+'.xlsx')

        writer = pd.ExcelWriter(full_path, engine='xlsxwriter')

        msd.to_excel(writer, sheet_name='Data', startrow=1)
        deff.to_excel(writer, sheet_name='Data', startrow=len(msd)+4)
        workbook = writer.book

        sheet_format = workbook.add_format({'align': 'center',
                                            'valign': 'vcenter'})
        header_format = workbook.add_format({'align': 'center',
                                             'valign': 'vcenter',
                                             'bold': 1})

        data_sheet = writer.sheets['Data']
        data_sheet.set_row(1, 21, header_format)
        data_sheet.set_row(len(msd)+4, 21, header_format)
        data_sheet.set_column(0, len(msd.columns), 15, sheet_format)

        data_sheet = writer.sheets['Data']

        msd_title = f'{msd.name} Data'
        data_sheet.merge_range(0, 0,
                               0, len(msd.columns),
                               msd_title, header_format)

        deff_title = f'{deff.name} Data'
        data_sheet.merge_range(len(msd)+3,
                               0,
                               len(msd) + 3,
                               len(msd.columns),
                               deff_title, header_format)

        self.make_chart(workbook, msd, 1)
        self.make_chart(workbook, deff, len(msd)+4)

        workbook.close()
        writer.save()

    def make_chart_LOG(self, workbook: xls.book,
                       data: pd.DataFrame,
                       start_row: int) -> None:
        """Creates a log-log plot from given data.

        Arguments:
            workbook {ExcelWriter.book} -- Excel file to add the chart.
            data {Dataframe} -- Data do populate the chart.
            data_name {str} -- Title of the data.
            startrow {int} -- Starting row for data entry.
        """

        # Create a chart object.
        chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})

        # Configure the series of the chart from the dataframe data.
        trendLine = False
        if data.name in ("MSD", "MSD-LOG"):
            trendLine = {
                'type': 'linear',
                'display_equation': True,
                'display_r_squared': True,
                'line': {'none': True},
                'data_labels': {'position': True}
            }

        columns = len(data.columns)
        for i in range(1, columns):
            chart.add_series({
                'name': ['Data', start_row, i],
                'categories': ['Data', start_row + 1, 0,
                               start_row + len(data), 0],
                'values': ['Data', start_row + 1, i,
                           start_row + len(data), i],
                'trendline': trendLine,
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
            'name': ['Data', 3, columns+3],
            'categories': ['Data', 4, columns+2, 5, columns+2],
            'values': ['Data', 4, columns+3, 5, columns+3],
            'line': {
                'color': 'black',
                'width': 1.25,
                'dash_type': 'square_dot'},
        })
        chart.add_series({
            'name': ['Data', 3, columns+4],
            'categories': ['Data', 4, columns+2, 5, columns+2],
            'values': ['Data', 4, columns+4, 5, columns+4],
            'line': {
                'color': 'red',
                'width': 1.25,
                'dash_type': 'square_dot'},
        })
        chart.add_series({
            'name': ['Data', 3, columns+5],
            'categories': ['Data', 4, columns+2, 5, columns+2],
            'values': ['Data', 4, columns+5, 5, columns+5],
            'line': {
                'color': 'black',
                'width': 1.25,
                'dash_type': 'square_dot'},
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

    def export_transport_mode(self, path: str, msd: pd.DataFrame):
        """Export 'Transport Mode Characterization' report.

        Arguments:
            path {str} -- Path to the report file.
            msd {pd.DataFrame} -- DataFrame containing MSD data.
        """
        file_name = "Transport Mode Characterization"
        full_path = os.path.join(path, file_name+".xlsx")

        writer = pd.ExcelWriter(full_path, engine='xlsxwriter')

        msd.to_excel(writer, sheet_name='Data', startrow=1)
        workbook = writer.book

        sheet_format = workbook.add_format({'align': 'center',
                                            'valign': 'vcenter'})
        header_format = workbook.add_format({'align': 'center',
                                             'valign': 'vcenter',
                                             'bold': 1})
        num_format = workbook.add_format({'align': 'center',
                                          'valign': 'vcenter',
                                          'num_format': 1})

        columns = len(msd.columns)
        data_sheet = writer.sheets['Data']
        data_sheet.set_row(1, 21, header_format)
        data_sheet.set_row(len(msd)+4, 21, header_format)
        data_sheet.set_column(0, columns, 15, sheet_format)

        data_sheet = writer.sheets['Data']

        msd_title = f'{msd.name} Data'
        data_sheet.merge_range(0, 0,
                               0, columns,
                               msd_title, header_format)

        # Add guide series data
        slope_data = self.get_slopes(msd)
        _, intercept = slope_data.mean().tolist()

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
            line, col+1, f'=0.9*{ref_cell}-0.2+{intercept}', num_format)
        data_sheet.write_formula(
            line, col+2, f'={ref_cell}+{intercept}', num_format)
        data_sheet.write_formula(
            line, col+3, f'=1.1*{ref_cell}+0.2+{intercept}', num_format)

        line += 1
        ref_cell = f'INDIRECT(ADDRESS({line+1},{col+1}))'
        data_sheet.write(
            line, col, '=2', num_format)
        data_sheet.write_formula(
            line, col+1, f'=0.9*{ref_cell}-0.2+{intercept}', num_format)
        data_sheet.write_formula(
            line, col+2, f'={ref_cell}+{intercept}', num_format)
        data_sheet.write_formula(
            line, col+3, f'=1.1*{ref_cell}+0.2+{intercept}', num_format)
        # ----------------------------

        self.make_chart_LOG(workbook, msd, 1)

        slope_data[0].to_excel(writer, index=False,
                               sheet_name='Characterization')

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

        immobile_low = self.config.immobile['min']
        immobile_high = self.config.immobile['max']
        subdiffusive_low = self.config.sub_diffusive['min']
        subdiffusive_high = self.config.sub_diffusive['max']
        diffusive_low = self.config.diffusive['min']
        diffusive_high = self.config.diffusive['max']
        active_low = self.config.active['min']

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

    def export_einstein_stokes(self, path: str, data):
        file_name = "Einstein-Stokes Calculations (D0_Dw & microviscosity)"
        full_path = os.path.join(path, file_name+'.xlsx')

        writer = pd.ExcelWriter(full_path, engine='xlsxwriter')

        # msd.to_excel(writer, sheet_name='Data', startrow=1)
        # deff.to_excel(writer, sheet_name='Data', startrow=len(msd)+4)
        workbook = writer.book

        # --------------------------------------------------------------------
        worksheet = workbook.add_worksheet('Microviscosity calculation')
        worksheet.hide_gridlines(2)
        worksheet.merge_range('A1:B3', '')
        worksheet.insert_image('A1', 'einstein-stokes_equation.png')
        # --------------------------------------------------------------------

        workbook.close()
        writer.save()
