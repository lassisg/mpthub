# MPT Analysis

The Multiple Particle Tracking Analysis app to help on the analysis of data from video microscopy.

There are 3 main sources for analysis:

-   Multiple particle tracking report file in .csv format generated from an ImageJ plugin (Mosaic);
-   Multiple particle tracking report file in .txt format generated from an ImageJ plugin (Mosaic) **\***;
-   Video file in .avi format (needs microscope data);
-   Video file in .lif format (containing microscope data in its metadata).

_**\* This .txt file format must be avoided as it is not well formated for analysis.**_

The first step is to add videos for analysis. The user may add as many video as he/she wants. There may be videos in different formats (.avi + .lif + .csv + .txt).

##### TODO: Add image (add video button)

At this point, the app should read the files data and present a table with the data for the user. If anything is missing, the user mus be informed somehow.

##### TODO: Add image (table view image)

Then, the user may check the data and complete it (in case it is necessary).

##### TODO: Add image (chack detail image)

All checked, the user can start analysis.

##### TODO: Add image (start analysis button image)

During analysis, the user is informed about the process with message in the statusbar.

##### TODO: Add image (statusbar image)

The analysis occur in a video basis, that is, each video is analyzed after the previous one.
For each video, it is possible to review the tracking parameters and change them, as described below.

### Review parameters

After starting the analysis process, the first frame is shown with the identified particles using the default configuration.

##### TODO: Add image (annotated frame image)

A sidebar with those configuration is shown by the image right side.

##### TODO: Add image (current video frame image)

If the user is satisfied with the particle identification, it is time to click on continue analysis button.

After each video analysis, the data table receives the information of how many valid trajectories were found.

##### TODO: Add image (analysis result on data table image)

At this time, the export report button is enabled.

##### TODO: Add image (individual export button image)

Then the next video starts pre-analysis and show first frame with identified particles (as shown before).

After all analysis are done, the export full report button is enabled.

##### TODO: Add image (full export button image)

### Export report

There are _**X**_ main reports to be exported:

-   Individual Particle Analysis (containing $MSD$ and $D_{eff}$ data and charts);
-   Transport Mode Characterization (containing $MSD$ log data, $MSD$ chart and diffusivity characterization);
-   Einstein-Stokes Calculations (containing $D_0$, $D_W$ & microviscosity calculations);

Besides the reports, for each videos there are trajectories images to be exported. Those images can be seen after analysis by clicking on each videos and selecting "Show detail".

##### TODO: Add image (show detail image)

A new window will show with every image for the selected video.

<!-- TODO: Write details and documentation -->
