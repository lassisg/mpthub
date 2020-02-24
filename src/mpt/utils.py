import pandas as pd
from pandas import ExcelWriter as xls
import os
import numpy as np


def rename_columns(data: pd.DataFrame) -> pd.DataFrame:
    columns_names = pd.Series(range(1, len(data.columns)+1))-1
    columns_names = [
        f'{data.name} {x+1} ({chr(956)}m{chr(178)})' for x in columns_names]
    columns_names[len(columns_names) -
                  1] = f'<{data.name}> ({chr(956)}m{chr(178)})'
    data.columns = columns_names

    return data


def get_slopes(dataIn: pd.DataFrame):
    return pd.Series([np.polyfit(dataIn[dataIn.columns[0]],
                                 np.asarray(dataIn[column]), 1)[0]
                      for column in dataIn.columns[1:-1]])


def make_chart(workbook: xls.book, data: pd.DataFrame, start_row: int):
    #       (workbook: xls.book, data: df, data_name: str, startrow: int):

    # Create a chart object.
    chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})
    mean_chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})

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


def get_diffusivity_ranges(CFG_PATH):
    return pd.read_json(os.path.join(CFG_PATH, "cfg-diffusivity.json"))
    # if ref == 0:
    #     return get_config('transport_mode', 'immobile_range')
    # elif ref == 1:
    #     return get_config('transport_mode', 'sub-diffusive_range')
    # elif ref == 2:
    #     return get_config('transport_mode', 'diffusive_range')

    # return get_config('transport_mode', 'active_range')


# def export_individual_particle_analysis(analysis, video_index):
def export_individual_particle_analysis(current_vid, path):
    # Individual Particle Analysis ------
    print("Exporting 'Individual Particle Analysis' report...")
    # current_vid = analysis.videos[video_index]
    # file_name = os.path.join(analysis.out_path,
    #                          current_vid.name + " - Individual Particle Analysis.xlsx")
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
    data_sheet.set_column(0, len(current_vid.msd.columns), 15, sheet_format)

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


# def export_transport_mode(analysis, video_index):
def export_transport_mode(current_vid, path):
    print("Export transport mode sheet")
    # current_vid = analysis.videos[video_index]
    current_vid.log_msd = np.log10(current_vid.msd.reset_index())
    current_vid.log_msd.name = current_vid.msd.name

    columns = current_vid.msd.shape[1]

    # file_name = os.path.join(analysis.out_path,
    #                          current_vid.name + " - Transport Mode Characterization.xlsx")
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

    data_sheet.merge_range(1, columns+2,
                           1, columns+5,
                           'Guides', header_format)

    data_sheet.merge_range(2, columns+2,
                           3, columns+2,
                           'x', header_format)

    data_sheet.merge_range(2, columns+3,
                           2, columns+5,
                           'y', header_format)

    data_sheet.write(3, columns+3, 'm=0.9', header_format)
    data_sheet.write(3, columns+4, 'm=1', header_format)
    data_sheet.write(3, columns+5, 'm=1.1', header_format)

    col = columns + 2
    line = 4
    ref_cell = f'INDIRECT(ADDRESS({line+1}, {col+1}))'

    data_sheet.write(line, col, '=-2', num_format)
    data_sheet.write_formula(
        line, col+1, f'=0.9*{ref_cell}-0.2+{b}', num_format)
    data_sheet.write_formula(line, col+2, f'={ref_cell}+{b}', num_format)
    data_sheet.write_formula(
        line, col+3, f'=1.1*{ref_cell}+0.2+{b}', num_format)

    line += 1
    ref_cell = f'INDIRECT(ADDRESS({line+1},{col+1}))'

    data_sheet.write(line, col, '=-2', num_format)
    data_sheet.write_formula(
        line, col+1, f'=0.9*{ref_cell}-0.2+{b}', num_format)
    data_sheet.write_formula(line, col+2, f'={ref_cell}+{b}', num_format)
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
    immobile_high = float('{0:.3g}'.format(diff_ranges.immobile.high-0.001))
    subdiffusive_low = float('{0:.1g}'.format(diff_ranges.sub_diffusive.low))
    subdiffusive_high = float('{0:.3g}'.format(
        diff_ranges.sub_diffusive.high-0.001))
    diffusive_low = float('{0:.2g}'.format(diff_ranges.diffusive.low))
    diffusive_high = float('{0:.3g}'.format(diff_ranges.diffusive.high-0.001))
    active_low = float('{0:.2g}'.format(diff_ranges.active.low))

    data_sheet.write('E2', f'{str(immobile_low)}-{str(immobile_high)}')
    data_sheet.write('E3', f'{str(subdiffusive_low)}-{str(subdiffusive_high)}')
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
