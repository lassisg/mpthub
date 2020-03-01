import json
import pandas as pd
import xlsxwriter
import numpy as np
import time
import os
import sys
from statistics import mean


def import_file(filename):

    f = open(filename)
    f_list = list(f)
    first_trajectory_row = f_list.index('%% Trajectory 1\n')
    f.close()

    rows_to_skip = first_trajectory_row + 1

    data = pd.read_csv(
        filename,
        skiprows=rows_to_skip,
        delim_whitespace=True,
        usecols=[1, 2],
        names=["x", "y"],
        decimal=",",
    )
    return data


def clean_data(data):
    data.loc[:, "x"].replace(
        to_replace="Trajectory", value="0", regex=True, inplace=True
    )

    # Delete rows that have the value 'frame'
    indexNames = data[data['x'] == 'frame'].index
    data.drop(indexNames, inplace=True)

    return data


def correct_separator(data):
    # data.loc[:, "x"].replace(to_replace=",", value=".",
    #                          regex=True, inplace=True)
    data.replace(to_replace=",", value=".",
                 regex=True, inplace=True)
    return data


def remove_index(data):
    data.reset_index(drop=True, inplace=True)
    return data


def add_label(data):
    data["x"] = pd.to_numeric(data["x"])
    data["y"] = pd.to_numeric(data["y"])
    return data


def split_trajectories(data):
    result = []
    last_index = 0
    for ind, row in data.iterrows():
        if data.loc[ind, "x"] == 0:
            index = ind
            result.append(data.iloc[last_index:index])
            last_index = ind + 1

    result.append(data.iloc[last_index:index])

    return result


def get_valid_trajectories(data):
    result = []
    for trajectory in data:
        if len(trajectory) >= 560:
            result.append(trajectory)

    return result


def compute_msd(data_list):

    trajectories = []
    msd = pd.DataFrame()
    i = 1
    for trace in data_list:
        frames = len(trace)
        t = tau[:frames]

        xy = trace.values

        trajectory = pd.DataFrame({"t": t, "x": xy[:, 0], "y": xy[:, 1]})

        # Compute MSD
        msdp = calc_msd(trajectory)
        msdm = msdp * (1 / 1.54 ** 2)

        msdm = msdm[:560]
        msd[i] = msdm
        i += 1

        trajectories.append(msd)

    return msd


def calc_msd(trajectory):
    shifts = trajectory["t"].index.values + 1
    msdp = np.zeros(shifts.size)
    for i, shift in enumerate(shifts):
        diffs_x = trajectory['x'] - trajectory['x'].shift(-shift)
        diffs_y = trajectory['y'] - trajectory['y'].shift(-shift)
        square_sum = np.square(diffs_x) + np.square(diffs_y)
        msdp[i] = square_sum.mean()

    return msdp


def calc_deff(deff):
    a = deff.values
    deff.iloc[:, 1:] = a[:, 1:] / (4 * a[:, 0, None])

    return deff


def rename_columns(data, data_name):
    columns_names = pd.Series(range(1, len(data.columns)+1))-1
    columns_names = [f'{data_name} {x} ({chr(956)}m²)' for x in columns_names]
    columns_names[0] = f'Timescale ({chr(120591)}) (s)'
    columns_names[len(columns_names)-1] = f'<{data_name}> ({chr(956)}m²)'
    data.columns = columns_names

    return data


def make_chart(workbook, data, data_name, startrow):
    # Create a chart object.
    chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})
    mean_chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})

    # Configure the series of the chart from the dataframe data.
    i = 2
    for column in data.columns[1:-1]:
        chart.add_series({
            'name': ['Data', startrow, i],
            'categories': ['Data', startrow+1, 1, startrow+len(data), 1],
            'values': ['Data', startrow+1, i, startrow+len(data), i],
        })
        i += 1

    mean_chart.add_series({
        'name': ['Data', startrow, i],
        'categories': ['Data', startrow+1, 1, startrow+len(data), 1],
        'values': ['Data', startrow+1, i, startrow+len(data), i],
    })

    # Add a chart title, style and some axis labels.
    chart.set_x_axis({'name': f'Time Scale ({chr(120591)}) (s)'})
    chart.set_y_axis({'name': f'{data_name} ({chr(956)}m²)'})
    chart.set_legend({'none': True})
    chart.set_style(1)

    # Add a chart title, style and some axis labels.
    mean_chart.set_title(
        {'name': f'Ensemble Data - <{data_name}> vs. Time Scale'})
    mean_chart.set_x_axis({'name': f'Time Scale ({chr(120591)}) (s)'})
    mean_chart.set_y_axis({'name': f'{data_name} ({chr(956)}m²)'})
    mean_chart.set_legend({'none': True})
    mean_chart.set_style(1)

    # Insert the chart into the worksheet.
    mean_time_chart = workbook.add_chartsheet(f'<{data_name}> vs Time')
    mean_time_chart.set_chart(mean_chart)

    # Insert the chart into the worksheet.
    time_chart = workbook.add_chartsheet(f'{data_name} vs Time')
    time_chart.set_chart(chart)


def export_individual_particle_analysis():
    writer = pd.ExcelWriter(OUT_PATH + 'Individual Particle Analysis.xlsx',
                            engine='xlsxwriter')

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
    data_sheet.set_column(0, 0, 4, sheet_format)
    data_sheet.set_column(1, 1, 15, sheet_format)
    data_sheet.set_column(2, len(msd.columns), 12, sheet_format)

    data_sheet = writer.sheets['Data']

    msd_title = 'MSD Data'
    data_sheet.merge_range(0, 0,
                           0, len(msd.columns),
                           msd_title, header_format)

    deff_title = 'Deff Data'
    data_sheet.merge_range(len(msd)+3, 0,
                           len(msd)+3, len(msd.columns),
                           deff_title, header_format)

    make_chart(workbook, msd, "MSD", 1)
    make_chart(workbook, deff, "Deff", len(msd)+4)

    workbook.close()
    writer.save()


def get_msd_slopes():
    return pd.Series([np.polyfit(log_msd[log_msd.columns[0]],
                                 np.asarray(log_msd[column]), 1)[0]
                      for column in log_msd.columns[1:-1]])


# TODO: Improve export function (characterization)
def export_characterization():
    writer = pd.ExcelWriter(OUT_PATH + 'Transport Mode Characterization.xlsx',
                            engine='xlsxwriter')

    slopes.to_excel(writer, index=False, sheet_name='Data')

    workbook = writer.book
    sheet_format = workbook.add_format(
        {'align': 'center', 'valign': 'vcenter'})
    header_format = workbook.add_format({'align': 'center', 'bold': 1})

    title = 'Slopes'
    data_sheet = writer.sheets['Data']
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

    immobile_low = float(get_transport_mode_ranges(0)[0])
    immobile_high = float('{0:.3g}'.format(
        get_transport_mode_ranges(0)[1]-0.001))
    subdiffusive_low = float('{0:.1g}'.format(get_transport_mode_ranges(1)[0]))
    subdiffusive_high = float('{0:.3g}'.format(
        get_transport_mode_ranges(1)[1]-0.001))
    diffusive_low = float('{0:.2g}'.format(get_transport_mode_ranges(2)[0]))
    diffusive_high = float('{0:.3g}'.format(
        get_transport_mode_ranges(2)[1]-0.001))
    active_low = float('{0:.1g}'.format(get_transport_mode_ranges(3)[0]))

    data_sheet.write('E2', f'{str(immobile_low)}-{str(immobile_high)}')
    data_sheet.write('E3', f'{str(subdiffusive_low)}-{str(subdiffusive_high)}')
    data_sheet.write('E4', f'{str(diffusive_low)}-{str(diffusive_high)}')
    data_sheet.write('E5', f'{str(active_low)}+')

    subdiffusive_txt = f'{str(subdiffusive_low).replace(".", ",")}'
    diffusive_txt = f'{str(diffusive_low).replace(".",",")}'
    active_txt = f'{str(active_low).replace(".",",")}'

    last_row = str(len(slopes)+1)
    data_sheet.write_formula('F2',
                             f'=COUNTIF(A2:A{last_row},"<{subdiffusive_txt}")')
    data_sheet.write_formula('F3',
                             f'=COUNTIFS(A2:A{last_row},">={subdiffusive_txt}",\
                             A2:A{last_row},"<{diffusive_txt}")')
    data_sheet.write_formula('F4',
                             f'=COUNTIFS(A2:A{last_row},">={diffusive_txt}",\
                             A2:A{last_row},"<{active_txt}")')
    data_sheet.write_formula('F5',
                             f'=COUNTIF(A2:A{last_row},">{active_txt}")')

    # Create a chart object.
    workbook.close()

    # Close the Pandas Excel writer and output the Excel file.
    writer.save()


def get_transport_mode_ranges(ref):

    if ref == 0:
        return get_config('transport_mode', 'immobile_range')
    elif ref == 1:
        return get_config('transport_mode', 'sub-diffusive_range')
    elif ref == 2:
        return get_config('transport_mode', 'diffusive_range')

    return get_config('transport_mode', 'active_range')


def get_config(config_group, config_name):

    with open('./src/res/mpt-config.json') as fh:
        config = json.load(fh)

    if (config_group in config):
        if (config_name in config[config_group]):
            return config[config_group][config_name]
    return None


def get_data_info(data_list):
    result = f"\nThe imported data file has \
                {len(data_list)} \
                good trajectories:\n\n"
    i = 1
    for data in data_list:
        result += f"Trajectory {i} contains {len(data)} frames.\n"
        i += 1

    return result


def export_data(data, filename):
    filename = f"{filename}.txt"
    data.to_csv(filename, sep=";", decimal=",", index=False)
    # data.to_csv("data_2.txt", sep=";", header=False)


# Programa beggining ----------------------------------------------------------
# dataFile = sys.argv[1]
rootPath = "D:/Cloud/Onedrive/Pessoal/Acadêmico/FEUP/2019-2020-PDISS_DISS/"
videoPath = "_research/Results/20200107/ImageJ/561_Mucus_D2/"
fileName = "results_561_Mucus_D2_Series001.txt"
dataFile = f"{rootPath}{videoPath}{fileName}"
# dataFile = './src/data/Movie78_NEW.txt'
data = import_file(dataFile)
data = clean_data(data)
data = correct_separator(data)
data = remove_index(data)
data = add_label(data)
data_list = split_trajectories(data)
data_list = get_valid_trajectories(data_list)

# MSD and Deff Calculation ----------------------------------------------------
# MSD - Parameters
video_len = get_config('microscopy', 'video_len')
total_frames = get_config('microscopy', 'total_frames')
max_time = video_len

time_step = max_time / total_frames
tau = np.linspace(time_step, max_time, total_frames)

msd = compute_msd(data_list)

# !: Remove when there is 100 real trajectories
# msd = pd.concat([msd, msd, msd, msd, msd, msd, msd,
#                  msd, msd, msd, msd], axis=1, ignore_index=True, sort=False)

tau = tau[:560]

msd.insert(0, "tau", tau, True)
msd = msd[msd[msd.columns[0]] < 10]

deff = calc_deff(msd.copy())

msd['mean'] = msd.iloc[:, 1:].mean(axis=1)
deff["mean"] = deff.iloc[:, 1:].mean(axis=1)

msd = rename_columns(msd, "MSD")
deff = rename_columns(deff, "Deff")

# Individual Particle Analysis ------------------------------------------------
OUT_PATH = os.getcwd() + '/data/export/'
export_individual_particle_analysis()

# Transport Mode Characterization ---------------------------------------------
log_msd = np.log10(msd)
slopes = get_msd_slopes()
export_characterization()

# Diffusion coefficients ------------------------------------------------------

# Effective diffusion coefficient ---------------------------------------------
# msd(τ) = 2dDτ
# d = dimensionality of the track (d=2 here in 2-dimensions)
# D = D0 = Deff = Effective diffusion coefficient
# τ = Time scale

# D = msd(τ) / 2dτ <=> Deff = MSD / 4τ

# Deff = MSD / 2dτ = Do
# Were normalized with the theoretical diffusion coefficient of the
# same size particles diffusing through water calculated using the
# Stokes–Einstein equation:
# D0 = (k_B T ) / 6 pi n a
# k_B: Boltzmann constant = 1.38064852 × 10-23 m2 kg s-2 K-1,
# T = temperature (consider 37°C = 310.15 K),
# h = fluid viscosity (0.000692 kg m-1 s-1 for water at 37°C )
# a = particle radius (consider 1,88*(10^-7)/2 m)
# D0 =


# -------------------------------------------------------------------- Dev
print(f"Total time spent: {time.process_time()}")
# ------------------------------------------------------------------------

# print(get_data_info(data_list))

# print(msd.to_json(orient="records"))
# sys.stdout.flush()
