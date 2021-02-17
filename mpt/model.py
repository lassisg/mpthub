import mpt.database as db
import pandas as pd
import numpy as np
import os
import locale
import trackpy as tp
import string
import itertools

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

    def update(self, new_config: pd.DataFrame) -> None:
        """Updates diffusivity ranges data on database."""
        self.config.to_sql('diffusivity', con=conn,
                           index=False, if_exists='replace')


class Analysis():

    def __init__(self) -> None:
        self.summary = pd.DataFrame()
        self.load_config()

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
        self.trajectories = pd.DataFrame(
            columns=['file_name', 'particle', 'frame', 'x', 'y'])
        self.valid_trajectories = self.trajectories.copy()

        i = 0
        for file in file_list:
            if not self.summary.empty:
                masked_df = self.summary.full_path == file
                if masked_df.any():
                    continue

            full_data = pd.read_csv(file)
            file_name, _ = os.path.splitext(os.path.basename(file))
            if set(['Trajectory', 'Frame', 'x', 'y']).issubset(
                    full_data.columns):

                raw_data = full_data.loc[:, ['Trajectory', 'Frame', 'x', 'y']]
                raw_data, i = self.prepare_for_track_py(raw_data, i)
                raw_data.insert(loc=0, column='file_name', value=file_name)
                self.trajectories = self.trajectories.append(
                    raw_data, ignore_index=True)

    def clear_summary(self):
        self.summary.drop(
            self.summary.index, inplace=True)

    def get_valid_trajectories(self) -> None:
        grouped_data = self.trajectories.groupby(
            ['file_name', 'particle'], as_index=False)['frame'].count()

        valid_grouped_data = grouped_data[grouped_data['frame']
                                          >= int(self.config.min_frames)]
        self.valid_trajectories = self.trajectories[
            self.trajectories['particle'].isin(valid_grouped_data['particle'])]

    def summarize(self) -> None:
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

    def start(self):
        self.compute_msd()
        self.compute_msd_log()
        self.compute_deff()

        self.msd = self.rename_columns(self.msd, "MSD")
        self.msd_log = self.rename_columns(self.msd_log, "MSD-LOG")
        self.deff = self.rename_columns(self.deff, "Deff")

    def compute_msd(self):

        max_lagtime = int(self.config.time / (self.config.delta_t / 1000))
        fps = 1000 / self.config.delta_t
        self.msd = tp.imsd(traj=self.valid_trajectories,
                           mpp=self.config.width_si/self.config.width_px,
                           fps=fps,
                           max_lagtime=max_lagtime)

        # msd.name = "MSD"
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
            # msd_log.reset_index()
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
            # return pd.DataFrame()

            self.deff = self.msd.iloc[:, :-1].div((4*self.msd.index), axis=0)
            # self.deff.name = "Deff"
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
        # header = data.name
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
            "Exporting 'Individual Particle Analysis' report...")
        report.export_individual_particle_analysis(
            parent.general.config.save_folder, self.msd, self.deff)

        parent.statusBar.SetStatusText(
            "Exporting 'Transport Mode Characterization' report...")
        report.export_transport_mode(
            parent.general.config.save_folder, self.msd_log)

        parent.statusBar.SetStatusText(
            "Exporting 'Stokes-Einstein' report...")
        report_data = {'deff': self.deff.iloc[:, -1].mean(),
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

        slope_data[0].to_excel(writer, index=False,
                               sheet_name='Characterization')

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

        characterization_sheet = writer.sheets['Characterization']
        characterization_sheet.set_column(0, 0, 4, header_format)
        characterization_sheet.set_column(0, 0, 12, sheet_format)
        characterization_sheet.set_column(3, 3, 18, sheet_format)
        characterization_sheet.set_column(4, 4, 12, sheet_format)
        characterization_sheet.set_column(5, 5, 7, sheet_format)

        characterization_sheet.write('A1', 'Slopes', header_format)
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
            itertools.chain(string.ascii_uppercase,
                            (''.join(pair) for pair in itertools.product(
                                string.ascii_uppercase, repeat=2))
                            ))[1:total_trajectories+1]

        # --------------------------------------------------------------- SLOPE
        characterization_sheet.write(
            'B1', 'Slopes (Excel)', header_format)
        excel_slopes = [f'B{x+min_row}' for x in list(
            range(total_trajectories))]
        slope_formulas = [
            f'=SLOPE(Data!{x}3:{x}305,Data!A3:A305)' for x in column_list]

        for cell, formula in zip(excel_slopes, slope_formulas):
            characterization_sheet.write_formula(cell, formula)

        # ------------------------------------------------------------------ R2
        characterization_sheet.write(
            'C1', f'R{chr(178)} (Excel)', header_format)
        excel_r2 = [f'C{x+min_row}' for x in list(
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

        file_name = "Stokes-Einstein Calculations (D0_Dw & microviscosity)"
        full_path = os.path.join(path, file_name+'.xlsx')

        writer = pd.ExcelWriter(full_path, engine='xlsxwriter')

        workbook = writer.book

        # --------------------------------------------------------------------
        worksheet = workbook.add_worksheet('Microviscosity calculation')
        worksheet.hide_gridlines(2)

        sheet_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter'})
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
        summary_val_1d_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'border': 1,
             'num_format': '0.0'})
        summary_val_4d_format = workbook.add_format(
            {'align': 'center',
             'valign': 'vcenter',
             'border': 1,
             'num_format': '0.0000'})
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

        worksheet.set_column('A:A', 16, sheet_format)
        worksheet.set_column('B:Z', 12, sheet_format)
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
        worksheet.write_formula('B9', '=0.0006913',
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

        # worksheet.merge_range('G1:I2', 'ImageJ report file', summary_format)
        worksheet.merge_range('J1:J2', '', summary_format)
        worksheet.write_rich_string('J1',
                                    summary_format, 'D',
                                    subscript_format, '0\n',
                                    summary_format, f'({chr(956)}m',
                                    superscript_format, '2',
                                    summary_format, '-s',
                                    superscript_format, '-1',
                                    summary_format, ')',
                                    summary_format)

        worksheet.merge_range('K1:K2', '', summary_format)
        worksheet.write_rich_string('K1',
                                    summary_format, 'D',
                                    subscript_format, '0\n',
                                    summary_format, '(m',
                                    superscript_format, '2',
                                    summary_format, '-s',
                                    superscript_format, '-1',
                                    summary_format, ')',
                                    summary_format)

        worksheet.merge_range('L1:L2', '', summary_format)
        worksheet.write_rich_string('L1',
                                    summary_format, 'D',
                                    subscript_format, '0',
                                    summary_format, ' / D',
                                    subscript_format, 'W',
                                    summary_format)

        worksheet.merge_range('M1:M2', '', summary_format)
        worksheet.write_rich_string('M1',
                                    summary_format, 'Viscosity\n',
                                    summary_format, '(Pa.s)',
                                    summary_format)

        worksheet.merge_range('N1:N2', '', summary_format)
        worksheet.write_rich_string('N1',
                                    summary_format, 'Viscosity\n',
                                    summary_format, '(Po)',
                                    summary_format)

        worksheet.merge_range('O1:O2', '', summary_format)
        worksheet.write_rich_string('O1',
                                    summary_format, 'Viscosity\n',
                                    summary_format, '(cPo)',
                                    summary_format)

        worksheet.write('J3',
                        data['deff'],
                        summary_val_4d_format)
        worksheet.write_formula('K3',
                                '=$J3/10^12',
                                summary_val_E_format)
        worksheet.write_formula('L3',
                                '=$J3/$E$5',
                                summary_val_4d_format)
        worksheet.write_formula('M3',
                                '=($B$6*$B$7)/(6*$B$8*$K3*$B$10)',
                                summary_val_9d_format)
        worksheet.write_formula('N3',
                                '=$M3*10',
                                summary_val_9d_format)
        worksheet.write_formula('O3',
                                '=$N3*100',
                                summary_val_1d_format)
        # TODO: For each file, write the next lines
        # for key, item in enumerate(data['summary'].values):
        #     i = key+3
        #     worksheet.merge_range(f'G{i}:I{i}',
        #                           item[0],
        #                           summary_file_format)
        #     worksheet.write(f'J{i}',
        #                     item[1],
        #                     summary_val_4d_format)
        #     worksheet.write_formula(f'K{i}',
        #                             f'=$J{i}/10^12',
        #                             summary_val_E_format)
        #     worksheet.write_formula(f'L{i}',
        #                             f'=$J{i}/$E$5',
        #                             summary_val_4d_format)
        #     worksheet.write_formula(f'M{i}',
        #                             f'=($B$6*$B$7)/(6*$B$8*$K{i}*$B$10)',
        #                             summary_val_9d_format)
        #     worksheet.write_formula(f'N{i}',
        #                             f'=$M{i}*10',
        #                             summary_val_9d_format)
        #     worksheet.write_formula(f'O{i}',
        #                             f'=$N{i}*100',
        #                             summary_val_1d_format)
        # --------------------------------------------------------------------

        writer.save()
