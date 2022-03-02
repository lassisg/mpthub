import mpt.database as db
import pandas as pd
import numpy as np
import os
import locale
import trackpy as tp
from string import ascii_uppercase
from itertools import chain, product

conn = db.connect()


class General():

    def __init__(self) -> None:
        # print("Initializing General app configuration object...")
        self.load_config()

    def load_config(self) -> None:
        """Loads configuration into a Series with data from database."""
        config_df = pd.read_sql_table("app_config", con=conn)
        self.config = config_df.iloc[0]

    def update(self) -> None:
        """Updates diffusivity ranges data on database."""
        new_config_df = self.config.to_frame(0).T
        new_config_df.to_sql('app_config', con=conn,
                             index=False, if_exists='replace')


class Diffusivity:

    def __init__(self) -> None:
        self.load_config()

    def load_config(self) -> None:
        """Loads configuration into a DataFrame with data from database."""
        self.config = pd.read_sql_table("diffusivity", con=conn)

    def update(self) -> None:
        """Updates diffusivity ranges data on database."""
        self.config.to_sql('diffusivity', con=conn,
                           index=False, if_exists='replace')


class Analysis():

    def __init__(self) -> None:
        self.summary = pd.DataFrame()
        self.load_config()
        self.trajectories = pd.DataFrame(
            columns=['file_name', 'particle', 'frame', 'x', 'y'])

    def load_config(self) -> None:
        """Loads configuration into a Series with data from database."""
        self.config = pd.read_sql_table("analysis_config", con=conn).squeeze()

    def update(self) -> None:
        """Updates analysis_config ranges data on database."""
        new_config_df = self.config.to_frame(0).T
        new_config_df.to_sql('analysis_config', con=conn,
                             index=False, if_exists='replace')

    def load_reports(self, file_list: list) -> None:
        """Loads '.csv' files into DB table 'trajectories' after filtering \
            by valid trajectories.

        Arguments:
            file_list {list} -- File path list to be imported.
        """

        i = 0
        for file in file_list:
            if not self.summary.empty:
                new_file_name, _ = os.path.splitext(os.path.basename(file))
                masked_df = self.summary['file_name'] == new_file_name
                if masked_df.any():
                    continue

            full_data = pd.read_csv(file)
            file_name, _ = os.path.splitext(os.path.basename(file))
            if set(['Trajectory', 'Frame', 'x', 'y']).issubset(
                    full_data.columns):

                raw_data = full_data.loc[:, ['Trajectory', 'Frame', 'x', 'y']]
                i = len(self.trajectories.groupby(
                    ['particle'], as_index=False).count()['particle'])

                raw_data, i = self.prepare_for_track_py(raw_data, i)
                raw_data.insert(loc=0, column='file_name', value=file_name)
                self.trajectories = self.trajectories.append(
                    raw_data, ignore_index=True)

        self.remove_gaps()

    def remove_gaps(self):
        self.trajectories['frame'] = self.trajectories.index.values

    def clear_summary(self):
        self.summary = self.summary.iloc[0:0]
        self.trajectories = self.trajectories.iloc[0:0]
        self.valid_trajectories = self.valid_trajectories.iloc[0:0]

    def remove_file_trajectories(self, file_name):
        trajectories_filter = self.trajectories['file_name'] != file_name
        valid_filter = self.valid_trajectories['file_name'] != file_name
        summary_filter = self.summary['file_name'] != file_name

        self.trajectories = (
            self.trajectories[trajectories_filter].reset_index(drop=True))
        self.valid_trajectories = (
            self.valid_trajectories[valid_filter].reset_index(drop=True))
        self.summary = self.summary[summary_filter].reset_index(drop=True)

    def get_valid_trajectories(self) -> None:
        grouped_data = self.trajectories.groupby(
            ['file_name', 'particle'], as_index=False)['frame'].count()

        valid_grouped_data = grouped_data[grouped_data['frame']
                                          >= int(self.config.min_frames)]
        self.valid_trajectories = self.trajectories[
            self.trajectories['particle'].isin(valid_grouped_data['particle'])]

        # self.valid_trajectories = self.trajectories[(
        #     self.trajectories['file_name'].isin(
        #         valid_grouped_data['file_name']) &
        #     self.trajectories['particle'].isin(
        #         valid_grouped_data['particle'])
        # )]

    def summarize(self) -> None:

        self.get_valid_trajectories()

        particles_per_file = (
            self.trajectories.groupby('file_name')['particle']
            .nunique()
            .to_frame()
            .rename(columns={"particle": "trajectories"}))

        valid_particles_per_file = (
            self.valid_trajectories.groupby('file_name')['particle']
            .nunique()
            .to_frame()
            .rename(columns={"particle": "valid"}))

        self.summary = (
            pd.concat([particles_per_file, valid_particles_per_file], axis=1)
              .fillna(0)
              .astype(int)
              .reset_index())

    def prepare_for_track_py(self, data_in, i):
        data_out = data_in.copy()
        original_particle = data_in.groupby(
            ['Trajectory'], as_index=False).count()['Trajectory'].values
        new_particle_ref = dict(
            zip(original_particle, range(i, len(original_particle) + i)))

        data_out['Trajectory'] = data_in['Trajectory'].map(new_particle_ref)

        data_out.rename(columns={"Trajectory": "particle",
                                 "Frame": "frame"}, inplace=True)
        i += len(original_particle)

        return data_out, i

    def start_trackpy(self):
        self.compute_msd_tp()
        self.compute_msd_log()
        self.compute_deff()

        self.msd = self.rename_columns(self.msd, "MSD")
        self.msd_log = self.rename_columns(self.msd_log, "MSD-LOG")
        self.deff = self.rename_columns(self.deff, "Deff")

    def compute_msd_tp(self):
        max_lagtime = int(self.config.time / (self.config.delta_t / 1000))
        # fps = 1000 / self.config.delta_t
        fps = self.config.fps
        self.msd = tp.imsd(traj=self.valid_trajectories,
                           mpp=self.config.width_si/self.config.width_px,
                           fps=fps,
                           max_lagtime=max_lagtime)

        self.msd = self.msd[self.msd.index.values < self.config.time]
        self.msd.index.name = f'Timescale ({chr(120591)}) (s)'
        self.msd.columns = [f'MSD {col}' for col in range(
            1, len(self.msd.columns)+1)]

        self.msd['MSD mean'] = self.msd.mean(axis=1)

        self.msd = self.msd.iloc[:max_lagtime, :]

    def compute_msd_log(self) -> None:
        """Computes the log version of Mean-squared Displacement.
        It is mandatory that the MSD is already computed.
        """
        if not self.msd.empty:
            self.msd_log = np.log10(self.msd.reset_index().iloc[:, :-1])
            self.msd_log.set_index(
                f'Timescale ({chr(120591)}) (s)', inplace=True)
            self.msd_log.name = "MSD-LOG"
            self.msd_log['mean'] = self.msd_log.mean(axis=1)

    def compute_deff(self) -> None:
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
        if not self.msd.empty:
            self.deff = self.msd.iloc[:, :-1].div((4*self.msd.index), axis=0)
            self.deff["mean"] = self.deff.mean(axis=1)

    def rename_columns(self, data: pd.DataFrame, header) -> pd.DataFrame:
        """Rename Pandas DataFrame columns to meaningfull names according \
            with the input's Pandas DataFrame name.

        Arguments:
            data {pd.DataFrame} -- Pandas DataFrame with columns in an \
                undesired naming.

        Returns:
            pd.DataFrame -- Input Pandas DataFrame with renamed \
                columns. No data changed.
        """
        unit = f"{chr(956)}m{chr(178)}"

        columns_names = pd.Series(range(1, len(data.columns)+1))-1
        columns_names = [f'{header} {x+1} ({unit})' for x in columns_names]
        columns_names[len(columns_names) - 1] = f'<{header}> ({unit})'

        data.columns = columns_names

        return data

    def get_timestamp_deffs(self):
        deff_index = self.deff.index.values

        analysis_timestamp = deff_index.flat[np.abs(
            deff_index - self.config.time).argmin()]

        analysis_d0 = self.deff.loc[analysis_timestamp][-1]

        return {'time': analysis_timestamp,
                'deff': analysis_d0}

    def export(self, parent):
        """Call specific export functions.
        """
        report = Report()

        parent.show_message(
            "Exporting 'Individual Particle Analysis' report...", 1000)
        report.export_individual_particle_analysis(
            parent.general.config.save_folder, self.msd, self.deff)

        parent.show_message(
            "Exporting 'Transport Mode Characterization' report...", 1000)
        report.export_transport_mode(
            parent.general.config.save_folder, self.msd_log)

        parent.show_message(
            "Exporting 'Stokes-Einstein' report...", 1000)

        report_data = {'deffs': self.get_timestamp_deffs(),
                       'p_size': self.config.p_size,
                       'temperature_C': self.config.temperature_C}
        report.export_einstein_stokes(
            parent.general.config.save_folder, report_data)


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

    def make_chart(self, workbook: pd.ExcelWriter,
                   data: pd.DataFrame,
                   data_name: str,
                   start_row: int) -> None:
        # TODO: Make function generic so it can be used for any chart
        """Create a chart for individual particle analysis.

        Arguments:
            workbook {pd.ExcelWriter} -- Excel spreadsheet object that will \
                hold the chart.
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
                'trendline': False})

        mean_chart.add_series({
            'name': ['Data', start_row, columns],
            'categories': ['Data', start_row+1, 0,
                           start_row+len(data), 0],
            'values': ['Data', start_row+1, columns,
                       start_row+len(data), columns]})

        # Add a chart title, style and some axis labels.
        axis_digits = np.ceil(-np.log10(
            np.abs(np.min(data.values)) -
            np.abs(np.floor(np.min(data.values))))) - 1
        y_axis_min = 1 / (10**(axis_digits+1))
        chart.set_x_axis({
            'num_format': '0.00',
            'max': round(max(data.index.values)*3),
            'min': 0.01,
            'crossing': 0.01,
            'log_base': 10,
            'name': f'Time Scale ({chr(120591)}) (s)'})
        chart.set_y_axis({
            'num_format': '0E-00',
            'min': y_axis_min,
            'max': round(max(data.index.values)*5),
            'crossing': y_axis_min,
            'log_base': 10,
            'name': f'{data_name} ({chr(956)}m²)'})
        chart.set_legend({'none': True})
        chart.set_style(1)

        # Add a chart title, style and some axis labels.
        mean_chart.set_title(
            {'name': f'Ensemble Data - <{data_name}> vs. Time Scale'})
        mean_chart.set_x_axis({
            'num_format': '0.00',
            'min': 0.01,
            'max': round(max(data.index.values)*3),
            'crossing': 0.01,
            'log_base': 10,
            'name': f'Time Scale ({chr(120591)}) (s)'})
        mean_chart.set_y_axis({
            'num_format': '0E-00',
            'min': y_axis_min,
            'max': round(max(data.index.values)*10),
            'crossing': y_axis_min,
            'log_base': 10,
            'name': f'{data_name} ({chr(956)}m²)'})
        mean_chart.set_legend({'none': True})
        mean_chart.set_style(1)

        # Insert the chart into the worksheet.
        mean_time_chart = workbook.add_chartsheet(f'<{data_name}> vs Time')
        mean_time_chart.set_chart(mean_chart)
        mean_time_chart.set_zoom(88)

        # Insert the chart into the worksheet.
        time_chart = workbook.add_chartsheet(f'{data_name} vs Time')
        time_chart.set_chart(chart)
        time_chart.set_zoom(84)

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

        msd.to_excel(writer, sheet_name='Data',
                     float_format='%.9f', startrow=1)
        deff.to_excel(writer, sheet_name='Data',
                      float_format='%.9f', startrow=len(msd)+4)
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

        msd_title = 'MSD Data'
        data_sheet.merge_range(0, 0,
                               0, len(msd.columns),
                               msd_title, header_format)

        deff_title = 'Deff Data'
        data_sheet.merge_range(len(msd)+3,
                               0,
                               len(msd) + 3,
                               len(msd.columns),
                               deff_title, header_format)

        self.make_chart(workbook, msd, "MSD", 1)
        self.make_chart(workbook, deff, "Deff", len(msd)+4)

        writer.save()

    def make_chart_LOG(self, workbook: pd.ExcelWriter,
                       data: pd.DataFrame,
                       data_name: str,
                       start_row: int) -> None:
        """Creates a log-log plot from given data.

        Arguments:
            workbook {pd.ExcelWriter} -- Excel file to add the chart.
            data {Dataframe} -- Data do populate the chart.
            data_name {str} -- Title of the data.
            startrow {int} -- Starting row for data entry.
        """

        # Create a chart object.
        chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})

        # Configure the series of the chart from the dataframe data.
        columns = data.shape[1]
        for i in range(1, columns + 1):
            chart.add_series({
                'name': ['Data', start_row, i],
                'categories': ['Data',
                               start_row + 1, 0,
                               start_row + len(data), 0],
                'values':     ['Data',
                               start_row + 1, i,
                               start_row + len(data), i]})

        line_colors = ['black', 'red', 'black']
        for i, line_color in zip(range(columns+3, columns+6),
                                 line_colors):
            chart.add_series({
                'name': ['Data', 3, i],
                'categories': ['Data', 4, columns+2, 5, columns+2],
                'values': ['Data', 4, i, 5, i],
                'line': {
                    'color': line_color,
                    'width': 1.25,
                    'dash_type': 'square_dot'}})

        # Add a chart title, style and some axis labels.
        axis_min_x = np.round(np.min(data.index.values)) - 1
        axis_max_x = np.round(np.max(data.index.values)) + 1
        axis_min_y = np.round(np.min(data.values)) - 1
        axis_max_y = np.round(np.max(data.values)) + 1

        chart.set_x_axis({
            'num_format': '0.00',
            'min': axis_min_x,
            'max': axis_max_x,
            'crossing': axis_min_x,
            'name': f'Time Scale ({chr(120591)}) (s)'})
        chart.set_y_axis({
            'num_format': '0.00',
            'min': axis_min_y,
            'max': axis_max_y,
            'crossing': axis_min_y,
            'name': f'{data_name} ({chr(956)}m²)'})
        chart.set_legend({'none': True})
        chart.set_style(1)

        # Insert the chart into the worksheet.
        time_chart = workbook.add_chartsheet(f'{data_name} vs Time')
        time_chart.set_chart(chart)
        time_chart.set_zoom(84)

    def export_transport_mode(self, path: str, msd: pd.DataFrame):
        """Export 'Transport Mode Characterization' report.

        Arguments:
            path {str} -- Path to the report file.
            msd {pd.DataFrame} -- DataFrame containing MSD data.
        """
        file_name = "Transport Mode Characterization"
        full_path = os.path.join(path, file_name+".xlsx")

        writer = pd.ExcelWriter(full_path, engine='xlsxwriter')

        msd.to_excel(writer, sheet_name='Data',
                     float_format="%.9f", startrow=1)
        workbook = writer.book

        sheet_format = workbook.add_format({'align': 'center',
                                            'valign': 'vcenter',
                                            'num_format': '0.000000000'})
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

        msd_title = 'MSD Data'
        # msd_title = f'{msd.name} Data'
        data_sheet.merge_range(0, 0,
                               0, columns,
                               msd_title, header_format)

        # Add guide series data
        slope_data = self.get_slopes(msd)
        _, intercept = slope_data.mean().tolist()

        data_sheet.merge_range(1, columns + 2,
                               1, columns + 5,
                               'Guides', header_format)
        data_sheet.merge_range(2, columns + 2,
                               3, columns + 2,
                               'x', header_format)
        data_sheet.merge_range(2, columns + 3,
                               2, columns + 5,
                               'y', header_format)

        alpha02 = 2 / 10
        alpha09 = 9 / 10
        alpha11 = 11 / 10

        data_sheet.write(3, columns+3,
                         f'm={locale.format_string("%.1f", alpha09)}',
                         header_format)
        data_sheet.write(3, columns+4, 'm=1', header_format)
        data_sheet.write(3, columns+5,
                         f'm={locale.format_string("%.1f", alpha11)}',
                         header_format)

        col = columns + 2
        line = 4
        x_axis_value = -2
        subdiffusive_y = alpha09*x_axis_value - alpha02 + intercept
        diffusive_y = x_axis_value + intercept
        active_y = alpha11*x_axis_value + alpha02 + intercept

        data_sheet.write(line, col, x_axis_value, num_format)
        data_sheet.write(line, col+1, subdiffusive_y, num_format)
        data_sheet.write(line, col+2, diffusive_y, num_format)
        data_sheet.write(line, col+3, active_y, num_format)

        line += 1
        x_axis_value = 1.5
        subdiffusive_y = alpha09*x_axis_value - alpha02 + intercept
        diffusive_y = x_axis_value + intercept
        active_y = alpha11*x_axis_value + alpha02 + intercept

        data_sheet.write(line, col, x_axis_value, num_format)
        data_sheet.write(line, col+1, subdiffusive_y, num_format)
        data_sheet.write(line, col+2, diffusive_y, num_format)
        data_sheet.write(line, col+3, active_y, num_format)
        # ----------------------------

        self.make_chart_LOG(workbook, msd, "MSD", 1)

        characterization_sheet = workbook.add_worksheet('Characterization')

        sheet_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'num_format': '0.000000000'})
        count_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'num_format': '0'})
        header_format = workbook.add_format(
            {'align': 'center', 'bold': 1})

        characterization_sheet.set_column(0, 0, 4, header_format)
        characterization_sheet.set_column(0, 1, 12, sheet_format)
        characterization_sheet.set_column(3, 3, 18, sheet_format)
        characterization_sheet.set_column(4, 4, 12, sheet_format)
        characterization_sheet.set_column(5, 5, 7, sheet_format)

        # characterization_sheet.write('A1', 'Slopes', header_format)
        characterization_sheet.write('D1', 'Transport Mode', header_format)
        characterization_sheet.write('E1', 'Slope', header_format)
        characterization_sheet.write('F1', 'Count', header_format)

        characterization_sheet.write('D2', 'Immobile')
        characterization_sheet.write('D3', 'Sub-diffusive')
        characterization_sheet.write('D4', 'Diffusive')
        characterization_sheet.write('D5', 'Active')

        # -------------------------------------------------------- SLOPE and R2
        min_row = 2
        total_trajectories = len(msd.columns)-1

        column_list = list(
            chain(ascii_uppercase,
                  (''.join(pair)
                   for pair in product(ascii_uppercase, repeat=2))))

        columns_xxx = list(
            chain(ascii_uppercase,
                  (''.join(pair)
                   for pair in product(ascii_uppercase, repeat=3))))
        columns_xxx = columns_xxx[len(ascii_uppercase):]

        column_list.extend(columns_xxx)
        column_list = column_list[1:total_trajectories+1]

        # --------------------------------------------------------------- SLOPE
        characterization_sheet.write(
            'A1', 'Slopes', header_format)
        excel_slopes = [f'A{x+min_row}' for x in list(
            range(total_trajectories))]
        slope_formulas = [
            f'=SLOPE(Data!{x}3:{x}305,Data!A3:A305)' for x in column_list]

        for cell, formula in zip(excel_slopes, slope_formulas):
            characterization_sheet.write_formula(cell, formula)

        # ------------------------------------------------------------------ R2
        characterization_sheet.write(
            'B1', f'R{chr(178)}', header_format)
        excel_r2 = [f'B{x+min_row}' for x in list(
            range(total_trajectories))]
        r2_formulas = [
            f'=RSQ(Data!{x}3:{x}305,Data!A3:A305)' for x in column_list]

        for cell, formula in zip(excel_r2, r2_formulas):
            characterization_sheet.write_formula(cell, formula)
        # ---------------------------------------------------------------------

        immobile_low = locale.format_string(
            "%.1f", self.config.immobile['min'])
        immobile_high = locale.format_string(
            "%.3f", self.config.immobile['max'])
        subdiffusive_low = locale.format_string(
            "%.1f", self.config.sub_diffusive['min'])
        subdiffusive_high = locale.format_string(
            "%.3f", self.config.sub_diffusive['max'])
        diffusive_low = locale.format_string(
            "%.1f", self.config.diffusive['min'])
        diffusive_high = locale.format_string(
            "%.3f", self.config.diffusive['max'])
        active_low = locale.format_string(
            "%.1f", self.config.active['min'])

        characterization_sheet.write(
            'E2', f'{str(immobile_low)}-{str(immobile_high)}')
        characterization_sheet.write(
            'E3', f'{str(subdiffusive_low)}-{str(subdiffusive_high)}')
        characterization_sheet.write(
            'E4', f'{str(diffusive_low)}-{str(diffusive_high)}')
        characterization_sheet.write(
            'E5', f'{str(active_low)}+')

        immobile_formula = f'=COUNTIF(A:A,"<{subdiffusive_low}")'
        subdiffusive_formula = f'=COUNTIFS(A:A,">={subdiffusive_low}",'
        subdiffusive_formula += f'A:A,"<{diffusive_low}")'
        diffusive_formula = f'=COUNTIFS(A:A,">={diffusive_low}",'
        diffusive_formula += f'A:A,"<{active_low}")'
        active_formula = f'=COUNTIF(A:A,">={active_low}")'

        characterization_sheet.write_formula(
            'F2', immobile_formula, count_format)
        characterization_sheet.write_formula(
            'F3', subdiffusive_formula, count_format)
        characterization_sheet.write_formula(
            'F4', diffusive_formula, count_format)
        characterization_sheet.write_formula(
            'F5', active_formula, count_format)

        # Statistical info
        summary_format = workbook.add_format(
            {'align': 'right',
             'valign': 'vcenter'})
        characterization_sheet.write('D8', '<slope> = ', summary_format)
        characterization_sheet.write('D9', 'N = ', summary_format)
        characterization_sheet.write('D10', 'STD = ', summary_format)

        characterization_sheet.write_formula('E8', '=AVERAGE(A:A)')
        characterization_sheet.write_formula('E9', '=COUNT(A:A)', count_format)
        characterization_sheet.write_formula('E10', '=STDEV(A:A)')

        writer.save()

    def export_einstein_stokes(self, path: str, data):

        file_name = "Stokes-Einstein Calculations (Deff_Dw)"
        full_path = os.path.join(path, file_name+'.xlsx')

        writer = pd.ExcelWriter(full_path, engine='xlsxwriter')

        workbook = writer.book

        sheet_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter'})
        title_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'text_wrap': True,
             'bold': True})
        left_format = workbook.add_format(
            {'align': 'left',
             'valign': 'vcenter'})
        equation_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'border': 1})
        caption_format = workbook.add_format(
            {'align': 'left',
             'bold': True,
             'valign': 'vcenter'})

        h20_table_header_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'bold': True,
             'border': 1})
        h20_table_subscript_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'bold': True,
             'font_script': 2,
             'border': 1})
        h2o_variable_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'border': 1})

        variable_format = workbook.add_format(
            {'align': 'left',
             'valign': 'vcenter',
             'border': 1})
        intermediate_val_E_format = workbook.add_format(
            {'align': 'right',
             'valign': 'vcenter',
             'bg_color': '#e6b8b7',
             'num_format': '##0.00000E+0',
             'border': 1})
        intermediate_val_2d_format = workbook.add_format(
            {'align': 'right',
             'valign': 'vcenter',
             'bg_color': '#e6b8b7',
             'num_format': '0.00',
             'border': 1})
        intermediate_val_7d_format = workbook.add_format(
            {'align': 'right',
             'valign': 'vcenter',
             'bg_color': '#e6b8b7',
             'num_format': '0.0000000',
             'border': 1})
        note_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'bg_color': 'yellow',
             'border': 1})
        input_lbl_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'bold': True,
             'bg_color': '#b8cce4'})
        info_lbl_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'bold': True,
             'bg_color': '#ffff66'})
        intermediate_lbl_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'bold': True,
             'bg_color': '#e6b8b7'})
        output_lbl_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'bold': True,
             'bg_color': '#d8e4bc'})
        dw_format = workbook.add_format(
            {'align': 'left',
             'valign': 'vcenter',
             'bg_color': '#d8e4bc'})
        output_val_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'bold': True,
             'bg_color': '#d8e4bc'})
        input_val_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'bg_color': '#b8cce4'})
        subscript_format = workbook.add_format(
            {'font_script': 2})
        superscript_format = workbook.add_format(
            {'font_script': 1})
        summary_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'bold': True,
             'border': 1,
             'text_wrap': True})
        # summary_file_format = workbook.add_format(
        #     {'align': 'left',
        #      'valign': 'vcenter',
        #      'border': 1})
        # summary_val_1d_format = workbook.add_format(
        #     {'align': 'center',
        #      'valign': 'vcenter',
        #      'border': 1,
        #      'num_format': '0.0'})
        summary_val_4d_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'border': 1,
             'num_format': '0.0000'})
        summary_val_5d_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'border': 1,
             'num_format': '0.00000'})
        summary_val_E_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'border': 1,
             'num_format': '##0.00000E+0'})
        summary_val_9d_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'border': 1,
             'num_format': '0.000000000'})

        worksheet = workbook.add_worksheet('Microviscosity calculation')
        h2o_viscosity_sheet = workbook.add_worksheet('H2O viscosity')

        h2o_viscosity_sheet.hide_gridlines(2)
        h2o_viscosity_sheet.set_column('A:Z', 10, sheet_format)
        h2o_viscosity_sheet.set_default_row(21)
        h2o_viscosity_sheet.set_row(0, 42)

        h2o_viscosity_sheet_title = 'Dimensionless viscosity of liquid '
        h2o_viscosity_sheet_title += 'water at 0.1 MPa'
        h2o_viscosity_sheet.merge_range('A1:C1',
                                        h2o_viscosity_sheet_title,
                                        title_format)

        h2o_viscosity_sheet.merge_range('A2:C4', '', sheet_format)
        formula_image = './mpt/assets/h2o_viscosity_equation.png'
        h2o_viscosity_sheet.insert_image('A2',
                                         formula_image,
                                         {'x_offset': 52, 'y_offset': 12,
                                          'x_scale': 1.0, 'y_scale': 1.0})

        h2o_viscosity_sheet.write('A5', 'i', h20_table_header_format)
        h2o_viscosity_sheet.write('A6', 1, h2o_variable_format)
        h2o_viscosity_sheet.write('A7', 2, h2o_variable_format)
        h2o_viscosity_sheet.write('A8', 3, h2o_variable_format)
        h2o_viscosity_sheet.write('A9', 4, h2o_variable_format)

        h2o_viscosity_sheet.write_rich_string('B5',
                                              h20_table_header_format, 'a',
                                              h20_table_subscript_format, 'i',
                                              h20_table_header_format)
        h2o_viscosity_sheet.write('B6', 280.68, h2o_variable_format)
        h2o_viscosity_sheet.write('B7', 511.45, h2o_variable_format)
        h2o_viscosity_sheet.write('B8', 61.131, h2o_variable_format)
        h2o_viscosity_sheet.write('B9', 0.45903, h2o_variable_format)

        h2o_viscosity_sheet.write_rich_string('C5',
                                              h20_table_header_format, 'b',
                                              h20_table_subscript_format, 'i',
                                              h20_table_header_format)
        h2o_viscosity_sheet.write('C6', -1.9, h2o_variable_format)
        h2o_viscosity_sheet.write('C7',  -7.7, h2o_variable_format)
        h2o_viscosity_sheet.write('C8',  -19.6, h2o_variable_format)
        h2o_viscosity_sheet.write('C9', -40, h2o_variable_format)

        h2o_viscosity_sheet.merge_range('A10:C10',
                                        'https://doi.org/10.1063/1.3088050',
                                        caption_format)

        worksheet.hide_gridlines(2)
        worksheet.set_column('A:Z', 16, sheet_format)
        worksheet.set_column('C:C', 7)
        worksheet.set_column('E:E', 7)

        worksheet.set_default_row(21)

        worksheet.merge_range('A1:B3', '', equation_format)
        formula_image = './mpt/assets/einstein-stokes_equation.png'
        worksheet.insert_image('A1',
                               formula_image,
                               {'x_offset': 52, 'y_offset': 21,
                                'x_scale': 1.2, 'y_scale': 1.2})

        worksheet.write_rich_string('A5',
                                    variable_format, 'D',
                                    subscript_format, 'W',
                                    variable_format, ' (m',
                                    superscript_format, '2',
                                    variable_format, ' s',
                                    superscript_format, '-1',
                                    variable_format, ')', variable_format)
        worksheet.write_rich_string('A6',
                                    variable_format, 'K',
                                    subscript_format, 'B',
                                    variable_format, ' (m',
                                    superscript_format, '2',
                                    variable_format, ' kg s',
                                    superscript_format, '-2',
                                    variable_format, ' K',
                                    superscript_format, '-1',
                                    variable_format, ')', variable_format)
        worksheet.write('A7', 'T (K)', variable_format)
        worksheet.write('A8', 'Pi', variable_format)
        worksheet.write_rich_string('A9',
                                    variable_format, 'H',
                                    subscript_format, '2',
                                    variable_format, 'O viscosity (Pa.s)',
                                    variable_format)
        worksheet.write('A10', 'Radius (m)', variable_format)

        worksheet.write_formula('B5', '=($B$6*$B$7)/(6*$B$8*B9*$B$10)',
                                intermediate_val_E_format)
        worksheet.write_formula('B6', '=1.3806488E-23',
                                intermediate_val_E_format)
        worksheet.write_formula('B7', '=$E$7+273.15',
                                intermediate_val_2d_format)
        worksheet.write_formula('B8', '=PI()',
                                intermediate_val_7d_format)

        h2o_1 = "'H2O viscosity'!B6*($B$7/300)^'H2O viscosity'!C6"
        h2o_2 = "'H2O viscosity'!B7*($B$7/300)^'H2O viscosity'!C7"
        h2o_3 = "'H2O viscosity'!B8*($B$7/300)^'H2O viscosity'!C8"
        h2o_4 = "'H2O viscosity'!B9*($B$7/300)^'H2O viscosity'!C9"
        h2o_viscosity_formula = f'=({h2o_1}+{h2o_2}+{h2o_3}+{h2o_4})*0.000001'

        worksheet.write_formula('B9',
                                h2o_viscosity_formula,
                                intermediate_val_7d_format)

        worksheet.write_formula('B10', '=($E$10*0.000000001)/2',
                                intermediate_val_7d_format)
        worksheet.merge_range('A11:B11', '', note_format)
        worksheet.write_rich_string('A11', 'NOTE: Pa.s = kg m',
                                    superscript_format, '-1', ' s',
                                    superscript_format, '-1',
                                    note_format)

        worksheet.write('A13', 'Input cells', input_lbl_format)
        worksheet.write('A14', 'Info cells', info_lbl_format)
        worksheet.write('A15', 'Intermediate cells', intermediate_lbl_format)
        worksheet.write('A16', 'Output cells', output_lbl_format)

        B13_text = 'These cells are used to input known values'
        B14_text = 'Informative cells to help understand the formula'
        B15_text = 'These are cells used for the calculation.'
        B15_text += ' Must not be changed!'
        B16_text = 'Desired results are in these cells.'
        worksheet.write('B13', B13_text, caption_format)
        worksheet.write('B14', B14_text, caption_format)
        worksheet.write('B15', B15_text, caption_format)
        worksheet.write('B16', B16_text, caption_format)

        worksheet.write_string('C5', "=>")
        worksheet.write_string('C7', "<=")
        worksheet.write_string('C10', "<=")

        worksheet.write('D5', '')
        worksheet.write_rich_string('D5',
                                    dw_format, 'D',
                                    subscript_format, 'W',
                                    dw_format, f' ({chr(956)}m',
                                    superscript_format, '2',
                                    dw_format, ' s',
                                    superscript_format, '-1',
                                    dw_format, ')', dw_format)
        worksheet.write('D7', "T (ºC)", left_format)
        worksheet.write('D10', "Diameter (nm)", left_format)

        worksheet.write('E5', "=$B$5*10^12", output_val_format)
        worksheet.write('E7', data['temperature_C'], input_val_format)
        worksheet.write('E10', data['p_size'], input_val_format)

        worksheet.merge_range('G1:G2', '', summary_format)
        worksheet.write_rich_string('G1',
                                    summary_format, 'Timestamp\n',
                                    summary_format, '(s)',
                                    summary_format)
        worksheet.merge_range('H1:H2', '', summary_format)
        worksheet.write_rich_string('H1',
                                    summary_format, 'D',
                                    subscript_format, 'eff\n',
                                    summary_format, f'({chr(956)}m',
                                    superscript_format, '2',
                                    summary_format, '-s',
                                    superscript_format, '-1',
                                    summary_format, ')',
                                    summary_format)

        worksheet.merge_range('I1:I2', '', summary_format)
        worksheet.write_rich_string('I1',
                                    summary_format, 'D',
                                    subscript_format, 'eff\n',
                                    summary_format, '(m',
                                    superscript_format, '2',
                                    summary_format, '-s',
                                    superscript_format, '-1',
                                    summary_format, ')',
                                    summary_format)

        worksheet.merge_range('J1:J2', '', summary_format)
        worksheet.write_rich_string('J1',
                                    summary_format, 'D',
                                    subscript_format, 'W',
                                    summary_format, ' / D',
                                    subscript_format, 'eff',
                                    summary_format)

        worksheet.write('G3',
                        data['deffs']['time'],
                        summary_val_5d_format)
        worksheet.write('H3',
                        data['deffs']['deff'],
                        summary_val_9d_format)
        worksheet.write_formula('I3',
                                '=$H3/10^12',
                                summary_val_E_format)
        worksheet.write_formula('J3',
                                '=$E$5/$H3',
                                summary_val_4d_format)

        writer.save()
