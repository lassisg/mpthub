# For compatibility with Python 2 and 3
from __future__ import division, unicode_literals, print_function

# import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from pandas import ExcelWriter as xls
from pandas import DataFrame as df
import numpy as np
import math
import pims
import trackpy as tp
import os
from readlif.reader import LifFile
# from scipy import ndimage
# from skimage import morphology, util, filters
import json
import time
# import sys
# from statistics import mean
# import xlsxwriter as xw


def set_status(status_text: str):
    print(status_text)


set_status("Imports done...")

set_status("Caching functions...")


def rename_columns(data: df, data_name: str) -> df:
    columns_names = pd.Series(range(1, len(data.columns)+1))-1
    columns_names = [
        f'{data.name} {x+1} ({chr(956)}m{chr(178)})' for x in columns_names]
    columns_names[len(columns_names) -
                  1] = f'<{data.name}> ({chr(956)}m{chr(178)})'
    data.columns = columns_names

    return data


def make_chart_LOG(workbook: xls.book, data: df, data_name: str, startrow: int):
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

    i = 1
    for column in data.columns[0:-2]:
        chart.add_series({
            'name': ['Data', startrow, i],
            'categories': ['Data', startrow+1, 0, startrow+len(data), 0],
            'values': ['Data', startrow+1, i, startrow+len(data), i],
            'trendline': trendLine,
        })
        i += 1

    # Add guides series
    chart.add_series({
        'name': ['Data', 3, len(data.columns)+2],
        'categories': ['Data', 4, len(data.columns)+1, 5, len(data.columns)+1],
        'values': ['Data', 4, len(data.columns)+2, 5, len(data.columns)+2],
        'line': {
            'color': 'black',
            'width': 1.25,
            'dash_type': 'square_dot'},
        # 'trendline': trendLine,
    })
    chart.add_series({
        'name': ['Data', 3, len(data.columns)+3],
        'categories': ['Data', 4, len(data.columns)+1, 5, len(data.columns)+1],
        'values': ['Data', 4, len(data.columns)+3, 5, len(data.columns)+3],
        'line': {
            'color': 'red',
            'width': 1.25,
            'dash_type': 'square_dot'},
        # 'trendline': trendLine,
    })
    chart.add_series({
        'name': ['Data', 3, len(data.columns)+4],
        'categories': ['Data', 4, len(data.columns)+1, 5, len(data.columns)+1],
        'values': ['Data', 4, len(data.columns)+4, 5, len(data.columns)+4],
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


def make_chart(workbook: xls.book, data: df, data_name: str, startrow: int):
    # Create a chart object.
    chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})
    mean_chart = workbook.add_chart({'type': 'scatter', 'subtype': 'smooth'})

    # Configure the series of the chart from the dataframe data.
    trendLine = False
    # if data.name in "MSD":
    #     trendLine = {
    #         'type': 'power',
    #         'display_equation': True,
    #         'line': {'none': True},
    #     }

    i = 1
    for column in data.columns[0:-1]:
        chart.add_series({
            'name': ['Data', startrow, i],
            'categories': ['Data', startrow+1, 0, startrow+len(data), 0],
            'values': ['Data', startrow+1, i, startrow+len(data), i],
            'trendline': trendLine,
        })
        i += 1

    mean_chart.add_series({
        'name': ['Data', startrow, i],
        'categories': ['Data', startrow+1, 0, startrow+len(data), 0],
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


def export_transport_mode(fileName: str, dataMSD: df):
    report_name = f"{fileName} - Transport Mode Characterization.xlsx"
    writer = pd.ExcelWriter(OUT_PATH + report_name, engine='xlsxwriter')

    dataMSD.to_excel(writer, sheet_name='Data', startrow=1, index=False)

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
    data_sheet.set_row(len(dataMSD)+4, 21, header_format)
    data_sheet.set_column(0, len(dataMSD.columns), 15, sheet_format)

    data_sheet = writer.sheets['Data']

    msd_title = f'{dataMSD.name} Data'
    data_sheet.merge_range(0, 0,
                           0, len(dataMSD.columns)-1,
                           msd_title, header_format)

    # Add guide series data
    data_sheet.merge_range(1, len(dataMSD.columns)+1,
                           1, len(dataMSD.columns)+4,
                           'Guides', header_format)

    data_sheet.merge_range(2, len(dataMSD.columns)+1,
                           3, len(dataMSD.columns)+1,
                           'x', header_format)

    data_sheet.merge_range(2, len(dataMSD.columns)+2,
                           2, len(dataMSD.columns)+4,
                           'y', header_format)

    data_sheet.write(3, len(dataMSD.columns)+2, 'm=0.9', header_format)
    data_sheet.write(3, len(dataMSD.columns)+3, 'm=1', header_format)
    data_sheet.write(3, len(dataMSD.columns)+4, 'm=1.1', header_format)

    data_sheet.write(4, len(dataMSD.columns)+1, '=-2', num_format)
    data_sheet.write_formula(4, len(dataMSD.columns)+2,
                             '=0.9*V5-0.2', num_format)
    data_sheet.write_formula(4, len(dataMSD.columns)+3, '=V5', num_format)
    data_sheet.write_formula(4, len(dataMSD.columns)+4,
                             '=1.1*V5+0.2', num_format)

    data_sheet.write(5, len(dataMSD.columns)+1, '=2', num_format)
    data_sheet.write_formula(5, len(dataMSD.columns)+2,
                             '=0.9*V6-0.2', num_format)
    data_sheet.write_formula(5, len(dataMSD.columns)+3, '=V6', num_format)
    data_sheet.write_formula(5, len(dataMSD.columns)+4,
                             '=1.1*V6+0.2', num_format)
    # ----------------------------

    make_chart_LOG(workbook, dataMSD, "LOG", 1)

    slopeData = get_slopes(log_msd)
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

    last_row = str(len(slopeData)+1)

    immobile_formula = f'=COUNTIF(A2:A{last_row},"<{subdiffusive_txt}")'
    subdiffusive_formula = f'=COUNTIFS(A2:A{last_row},">={subdiffusive_txt}",'
    subdiffusive_formula += f'A2:A{last_row},"<{diffusive_txt}")'
    diffusive_formula = f'=COUNTIFS(A2:A{last_row},">={diffusive_txt}",'
    diffusive_formula += f'A2:A{last_row},"<{active_txt}")'
    active_formula = f'=COUNTIF(A2:A{last_row},">{active_txt}")'

    data_sheet.write_formula('F2', immobile_formula)
    data_sheet.write_formula('F3', subdiffusive_formula)
    data_sheet.write_formula('F4', diffusive_formula)
    data_sheet.write_formula('F5', active_formula)

    workbook.close()
    writer.save()


def export_individual_particle_analysis(fileName: str, dataMSD: df, dataDeff: df):
    writer = pd.ExcelWriter(OUT_PATH + fileName + ' - Individual Particle Analysis.xlsx',
                            engine='xlsxwriter')

    dataMSD.to_excel(writer, sheet_name='Data', startrow=1)
    dataDeff.to_excel(writer, sheet_name='Data', startrow=len(dataMSD)+4)

    workbook = writer.book
    sheet_format = workbook.add_format({'align': 'center',
                                        'valign': 'vcenter'})
    header_format = workbook.add_format({'align': 'center',
                                         'valign': 'vcenter',
                                         'bold': 1})

    data_sheet = writer.sheets['Data']
    data_sheet.set_row(1, 21, header_format)
    data_sheet.set_row(len(dataMSD)+4, 21, header_format)
    # data_sheet.set_column(0, 0, 15, sheet_format)
    # data_sheet.set_column(1, len(dataMSD.columns), 12, sheet_format)
    data_sheet.set_column(0, len(dataMSD.columns), 15, sheet_format)

    data_sheet = writer.sheets['Data']

    msd_title = f'{dataMSD.name} Data'
    data_sheet.merge_range(0, 0,
                           0, len(dataMSD.columns),
                           msd_title, header_format)

    deff_title = f'{dataDeff.name} Data'
    data_sheet.merge_range(len(dataMSD)+3, 0,
                           len(dataMSD)+3, len(dataMSD.columns),
                           deff_title, header_format)

    make_chart(workbook, dataMSD, dataMSD.name, 1)
    make_chart(workbook, dataDeff, dataDeff.name, len(dataMSD)+4)

    workbook.close()
    writer.save()


def get_config(config_group: str, config_name: str):

    with open(CFG_PATH + 'mpt-config.json') as fh:
        config = json.load(fh)

    if (config_group in config):
        if (config_name in config[config_group]):
            return config[config_group][config_name]
    return None


def get_transport_mode_ranges(ref: int):

    if ref == 0:
        return get_config('transport_mode', 'immobile_range')
    elif ref == 1:
        return get_config('transport_mode', 'sub-diffusive_range')
    elif ref == 2:
        return get_config('transport_mode', 'diffusive_range')

    return get_config('transport_mode', 'active_range')


def get_slopes(dataIn: df):
    return pd.Series([np.polyfit(dataIn[dataIn.columns[0]],
                                 np.asarray(dataIn[column]), 1)[0]
                      for column in dataIn.columns[1:-1]])


print("Functions cached...")

set_status("Loading file...")

densOpt = {
    "D2": {"name": "high", "abbrev": "D2"},
    "D3": {"name": "low", "abbrev": "D3"}
}

# bioMean = "H2O"
bioMean = "Mucus"
dens = densOpt['D2']

rootPath = "D:/Videos/i3S_Microscopy_Videos/"
videoPath = f"20200107/20200107-{bioMean}/561_{bioMean}_{dens['name']}Concentration/"
lifFile = f"561_{bioMean}_{dens['abbrev']}"

file = LifFile(f"{rootPath}{videoPath}{lifFile}.lif")

set_status("File loaded...")

# set up display area to show dataframe in jupyter qtconsole
# pd.set_option('display.max_rows', 500)
# pd.set_option('display.max_columns', 50)
# pd.set_option('display.width', 1000)

# Initial setup
OUT_PATH = os.getcwd() + '/data/export/'
CFG_PATH = os.getcwd() + '/'
# tp.utils.suppress_plotting()
f_size = 11
min_frame_seq = 560

msd_full = pd.DataFrame()
deff_full = pd.DataFrame()

fps = sum(image['scale'][-1] for image in file.image_list)/file.num_images
tau = 1 / fps

set_status("Ready to roll...")

set_status("Starting loop through '.tif' files...")
i = 0
for image in file.get_iter_image():
    if i > 0:
        break

    i += 1

    set_status("Getting data from '.tif' file...")
    total_frames = image.nt
    imwidth = image.dims[0]
    pxwidth = math.floor(imwidth / image.scale[0])

    print(
        f"\nSummary {image.name} -----------------------------------------\n")
    print(f"TIF file name: \t\t{lifFile}_{image.name}.tif")
    print(f"Frames in this video: \t{total_frames}")
    print(f"Digital video width: \t{imwidth} px")
    print(f"Real video width: \t{pxwidth} microns")
    print(f"Frames per second: \t{fps} fps\n")

    frames = pims.open(f"{rootPath}{videoPath}{lifFile}_{image.name}.tif")
    # frames[0]

    # ============================== Locate Features (particles)
    print("Locating particles...")
    f = tp.locate(frames[0], f_size)
    tp.annotate(f, frames[0])

    # ============================== Refine parameters
    set_status("Refining parameters...")
    m_mass = math.ceil(f.mass.mean())
    m_size = math.floor(f.size.mean())
    m_ecc = f.ecc.mean()

    # ============================== Relocate features according to mass
    set_status(f"Relocating particles...\n")
    f = tp.locate(frames[0], f_size, minmass=m_mass)
    tp.annotate(f, frames[0])

    # ============================== Subpixel accuracy
    tp.subpx_bias(f)

    # ============================== Locate features in all frames
    set_status(f"\nLocating particles in all frames...")
    f = tp.batch(frames[:], f_size, minmass=m_mass)

    # ============================== Link features into particle trajectories
    set_status("Linking particles into trajectories...")
    t = tp.link(f, f_size, memory=0)

    # ============================== Filter spurious trajectories
    set_status("Filtering trajectories...")
    t1 = tp.filter_stubs(t, min_frame_seq)

    # Compare the number of particles in the unfiltered and filtered data.
    print(f"Before: {t['particle'].nunique()}")
    print(f"After: \t{t1['particle'].nunique()}")

# if t1['particle'].nunique() > 0:
    if t1['particle'].nunique() == 0:
        continue

    # Convenience function -- just plots size vs. mass
    tp.mass_size(t1.groupby('particle').mean())

    # mass: brightness of the particle
    # size: diameter of the particle
    # ecc: eccentricity of the particle (0 = circular)
    t2 = t1[(
        (t1['mass'] > m_mass) &
        (t1['size'] < m_size) &
        (t1['ecc'] < m_ecc))]
    tp.annotate(t2[t2['frame'] == 0], frames[0])

    # ax = tp.plot_traj(t2)
    # plt.show()

    # ============================== Remove overall drift
    set_status("Removing drift...")
    drift = tp.compute_drift(t2)
    drift.plot()
    plt.show()

    tm = tp.subtract_drift(t2.copy(), drift)
    ax = tp.plot_traj(tm)
    plt.show()

    # ============================== Analyze trajectories
    set_status("Analyzing trajectories...")
    mpp = pxwidth/imwidth
    mlt = math.ceil(fps*10)  # Time to use (10s, 1s, 0.1s)

    im = tp.imsd(tm, mpp, fps, mlt)

    fig, ax = plt.subplots()
    ax.plot(im.index, im, 'k-', alpha=0.1)  # black lines, semitransparent
    ax.set(ylabel=r'MSD [$\mu$m$^2$]', xlabel='Timescale ($\\tau$) [$s$]')
    ax.set_xscale('log')
    ax.set_yscale('log')

    # ============================== Ensemble Mean Squared Displacement
    # em = tp.emsd(tm, mpp, fps, mlt)
    em = im.mean(axis=1)

    fig, ax = plt.subplots()
    ax.plot(em.index, em, 'o')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set(ylabel=r'MSD [$\mu$m$^2$]', xlabel='Timescale ($\\tau$) [$s$]')

    plt.figure()
    plt.title('Ensemble Data - <MSD> vs. Time Scale')
    plt.ylabel(r'MSD [$\mu$m$^2$]')
    plt.xlabel('Timescale ($\\tau$) [$s$]')
    tp.utils.fit_powerlaw(em)  # performs linear best fit in log space, plots

    # My code ---------------------------------------------------
    msd = im.copy()
    msd.name = "MSD"
    msd.index.name = f'Timescale ($\tau$) (s)'

    # msd_full = pd.concat([msd_full, msd], axis=1, sort=False)
    msd_full = pd.concat(
        [msd_full, msd],
        axis=1,
        ignore_index=True,
        sort=False)

   # Best option ?
    # msd['mean'] = em.values

    # In case fps changes between '.tif' files
    msd['mean'] = im.mean(axis=1)

    deff = msd.div((4*msd.index), axis=0)
    deff.name = "Deff"

    # TODO: Remove 2nd parameter (use the variable name)
    msd = rename_columns(msd, "MSD")
    deff = rename_columns(deff, "Deff")

    # msd = msd.reset_index()
    # deff = deff.reset_index()

    # Individual Particle Analysis ------
    reportName = f"{lifFile}_{image.name}"
    set_status("Exporting 'Individual Particle Analysis' report...")
    export_individual_particle_analysis(reportName, msd, deff)

    # Transport Mode Characterization ----
    log_msd = np.log10(msd.reset_index())
    log_msd.name = msd.name
    slopes = get_slopes(log_msd)
    set_status("Exporting 'Transport Mode Characterization' report...")
    export_transport_mode(reportName, log_msd)

    set_status("Image processed...")

print(f"\nExporting full data ---------------------------------------\n")
set_status(f"Gathering information...")

msd_full['mean'] = msd_full.mean(axis=1)
deff_full = msd_full.div((4*msd_full.index), axis=0)

# TODO: Remove 2nd parameter (use the variable name)
msd_full = rename_columns(msd_full, "MSD")
deff_full = rename_columns(deff_full, "Deff")

msd_full.reset_index(inplace=True)
deff_full.reset_index(inplace=True)

# Individual Particle Analysis ------
set_status("Exporting full 'Individual Particle Analysis' report...")
export_individual_particle_analysis(lifFile, msd_full, deff_full)
msd_full.head()

# Transport Mode Characterization ----
log_msd_full = np.log10(msd_full)

slopesFull = get_slopes(log_msd_full)
slopesFull

set_status("Exporting full 'Transport Mode Characterization' report...")
export_characterization(lifFile, log_msd_full)
set_status(f"\nExporting file success...\n")

print(f"\nFinish ----------------------------------------------------\n")
elapsed_time = time.strftime("%H:%M:%S", time.gmtime(time.process_time()))
set_status(f"Elapsed time: {elapsed_time}")
print(f"\n-----------------------------------------------------------\n")
