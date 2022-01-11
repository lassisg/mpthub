# MPT Analysis

The Multiple Particle Tracking Analysis application that generates reports with organized information about particle displacement, to help on the analysis of data from video microscopy analysis generated by ImageJ (using Mosaic plugin).

The application relies on the following workflow:

1. Solution preparation;
2. Video acquisition;
3. Video analysis (using ImageJ with Mosaic plugin);
4. Data analysis (performed by this app and described bellow).

## App installation

Just download the latest version for your Operating System and use. No need for installation.

## App usage

This application reads an ImageJ report. It only accept the file generated by 'All Trajectories to Table' button on the Mosaic plugin. As this is a '.csv' file, just this file format is allowed. If, however, any other file is used, the application should just ignore.

## The workflow

### 1. Review configuration

There are some configurations that need to exist in order to allow the app to make its calculations. There are 3 main configuration groups:

#### 1.1. App configuration

The App configuration basically means input and output folder. The App saves this folder's path in a way to make it easy for the user.
We understand that the user may have a specific folder with result files (from ImageJ) and a different one for report files (from this App).
The default configurations are:

| Operating System | Input folder                 | Output folder                        |
| ---------------- | ---------------------------- | ------------------------------------ |
| Windows          | C:\\Users\\\<username>\\.mpt | C:\\Users\\\<username>\\.mpt\\export |
| Linux            | /home/\<username>/.mpt       | /home/\<username>/.mpt/export        |
| Mac OS           | /Users/\<username>/.mpt      | /Users/\<username>/.mpt/export       |

If those folders don't exist, they will be created at first App use.
_**The values are saved each time the user uses the App.**_

#### 1.2. Analysis configuration

This configurations relate to the video acquisition parameters (except for the particle size, that usually comes from known particle size provided by manufacturer).

The default values are:
| Configuration          | Description                                                                                      | Default value |
| ---------------------- | ------------------------------------------------------------------------------------------------ | :-----------: |
| Size                   | Particle size (in SI unit <em>nm</em>)                                                           |      200      |
| Filter                 | Minimum number of consecutive frames a trajectory must have to be considered valid for analysis. |      590      |
| FPS                    | Frames per second used during video acquisition.                                                 |      30       |
| Total frames           | Total number of frames in video.                                                                 |      606      |
| Width (<em>px</em>)    | Width of the acquired video, in pixels.                                                          |      512      |
| Width (<em>&mu;m</em>) | Width of the acquired video, in SI unit <em>&mu;m</em>.                                          |      160      |

Those values are pre-defined based on previous experiment and can be changed in the App.

The values can be changed, as seen in the screenshot bellow.

![general_config](./docs/assets/general_config.png "General configuration")

#### 1.3. Diffusivity ranges configuration

As one of the report generated by the App is about diffusivity, the _Transport Mode Characterization_ ranges are essential.

The default values are:
| Transport Mode | Low value | High value |
| -------------- | :-------: | :--------: |
| Immobile       |    0.0    |   0.199    |
| Sub-diffusive  |    0.2    |   0.899    |
| Diffusive      |    0.9    |   1.199    |
| Active         |    1.2    |    1.2+    |

The values can be changed, as seen in the screenshot bellow.

![diffusivity_config](./docs/assets/diffusivity_config.png "Diffusivity ranges configuration")

---

### 2. Read the file(s)

By clicking on the 'Import files...' sub-menu, under 'File' menu, a dialog appears. This dialog allows the user to import multiple files.

![file_import](./docs/assets/File_menu_import.png "File menu (Import files)")

After reading the files, a summary table will show at the main window. This table shows the file name, total trajectories and valid trajectories is displayed on screen. At the bottom of the list, a total is displayed. For statistical purposes, approximately 100 valid trajectories must exist.

![files_summary](./docs/assets/files_summary.png "Files summary")

---

### 3. Start analysis

Configuration reviewed, reports loaded to app, it is time to make some math.
Under 'Tools' menu, 'Start analysis' sub-menu starts analysis. This sub-menu is disable at startup and only becomes enabled if the previous step occurs with no errors.

Disabled menu:
![start_analysis-disabled](./docs/assets/Start_analysis-disabled.png "Start analysis (disabled)")

Enabled menu:
![start_analysis-enabled](./docs/assets/Start_analysis-enabled.png "Start analysis (enabled)")

As the 'Start analysis' sub-menu, both 'Remove selected' and 'Clear summary' sub-menus are also enabled/disabled according to data imported.

The app must process the data from those files and perform a series of calculations, described bellow:

- Keep only those trajectories longer than the minimum frame number defined by the filter configuration.
- Compute MSD (mean squared displacement) for the group of results (near 100 trajectories)
- Compute <em>D<sub>eff</sub></em> (effective diffusivity) for the group of results (near 100 trajectories)
- Compute the slope (<em>&alpha;</em>) for each trajectory

When the analysis process is complete, the status bar will show a message to inform the user.

![analysis_complete](./docs/assets/Analysis_complete.png "Analysis complete")

---

### 4. Export reports

Now that analysis has been done, the user may export the reports. As before, the 'Save' sub-menu, under 'File' menu is disabled at startup. It becomes enabled only after analysis, if ok.

Disabled menu:
![export_results-disabled](./docs/assets/File_menu_export-disabled.png "Export results (disabled)")

Enabled menu:
![export_results-enabled](./docs/assets/File_menu_export-enabled.png "Export results (enabled)")

There are currently 3 reports available:

#### 4.1. Individual Particle Analysis

This report contains 5 sheets, described bellow:

![mode_sheets](./docs/assets/Individual_Particle_Analysis-sheets.png "Individual Particle Analysis report sheets")

##### 4.1.1. Data

This sheet contains the data from each valid trajectory Mean-squared Displacement (MSD) and Diffusivity efficiency coefficient (<em>D<sub>eff</sub></em>).

![mode_data](./docs/assets/Individual_Particle_Analysis-data.png "Individual Particle Analysis report data")

##### 4.1.2. \<MSD> vs Time

This sheet contains the Ensemble Mean-squared Displacement (\<MSD>) plot.

![ensemble_msd](./docs/assets/Ensemble_MSD_plot.png "Ensemble MSD plot")

##### 4.1.3. MSD vs Time

This sheet contains the MSD (Mean-squared Displacement) plot with all trajectories.

![individual_msd_plot](./docs/assets/Individual_MSD_plot.png "Individual MSD plot")

##### 4.1.4. \<<em>D<sub>eff</sub></em>> vs Time

This sheet contains the Ensemble effective diffusivity (\<<em>D<sub>eff</sub></em>>) chart.

![ensemble_deff](./docs/assets/Ensemble_Deff_plot.png "Ensemble Deff plot")

##### 4.1.5. <em>D<sub>eff</sub></em> vs Time

This sheet contains the effective diffusivity (<em>D<sub>eff</sub></em>) plot with all trajectories.

![individual_deff_plot](./docs/assets/Individual_Deff_plot.png "Individual Deff plot")

#### 4.2. Transport Mode Characterization

This report have 3 sheets, described bellow:

![mode_sheets](./docs/assets/Transport_Mode_Characterization-sheets.png "Transport Mode Characterization report sheets")

##### 4.2.1. Data

This sheet contains the data from each valid trajectory Mean-squared Displacement (MSD) in logarithm scale.

![mode_data](./docs/assets/Transport_Mode_Characterization-data.png "Transport Mode Characterization report data")

##### 4.2.2. MSD vs Time

This sheet contains the Mean-squared Displacement (MSD) log-log plot with all trajectories.

![mode_msd](./docs/assets/Transport_Mode_Characterization-plot.png "Transport Mode Characterization report MSD plot (log-log)")

##### 4.2.3. Characterization

This sheet contains:

- List os all valid trajectories slopes;
- Transport Mode Characterization table count;
- Summary information:
  - **\<slope>**: Slope average;
  - **N**: Number of slopes (equal number of valid trajectories);
  - **STD**: Standard Deviation.

![mode_chararcterization](./docs/assets/Transport_Mode_Characterization-chararcterization.png "Transport Mode Characterization report sheets")

#### 4.3. Einstein-Stokes Calculation - D0_Dw-Microviscosity

This report has only 1 sheet, named _**Microviscosity**_.
It contains the data for calculating microviscosity, <em>D<sub>0</sub>/D<sub>W</sub></em> ratio and some other intermediate calculations.
For the Einstein-Stokes, the particle size is considered to be of <em>200 nm</em>\*.

**\*The particle size can be changed, as mentioned on item _1.2. Analysis configuration_**

![Einstein-Stokes](./docs/assets/Einstein-Stokes.png "Einstein-Stokes")
