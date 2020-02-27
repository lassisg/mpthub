# from readlif.reader import LifFile
import math
import skvideo.io
import pandas as pd
import exifread
# import skvideo.datasets
# import skvideo.utils
import pims
import matplotlib
from matplotlib import pyplot as plt
import trackpy as tp

from math import ceil
matplotlib.use('WXAgg')


class Analysis():
    def __init__(self) -> None:
        self.config_path = ""
        self.full_path = ""
        self.file_path = ""
        self.file_name = ""
        self.file_ext = ""
        self.width_px = 0
        self.height_px = 0
        self.width_SI = 0
        self.height_SI = 0
        self.mpp = None
        self.frames = None
        self.time_lag = None
        self.fps = 30
        self.filter = 590
        self.f_size = 11
        self.m_mass = None
        self.m_size = None
        self.m_ecc = None
        # self.mlt = 0.0
        # self.features = pd.DataFrame()  # particles
        # self.trajectories = pd.DataFrame()
        # self.msd = pd.DataFrame()
        # self.deff = pd.DataFrame()
        # self.feature_size = 11
        # self.min_frame_seq = 0

    def from_csv(self):
        data = pd.read_csv(
            self.full_path,
            skiprows=1,
            usecols=[0, 1, 2, 3],
            names=["trajectory", "frame", "x", "y"],
            # decimal=",",
        )
        return data

    def from_tif(self):
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

    def from_avi(self):
        pass

    # def get_data(self):

    #     is_valid = False

    #     if self.extension == ".tif" or self.extension == ".tiff":
    #         self.read_tif_data()
    #         is_valid = True
    #     # TODO: Find a way to run without the need to create tif files
    #     # elif self.extension == ".lif":
    #         # self.read_lif_data()
    #     elif self.extension == ".avi":
    #         self.read_avi_data()
    #         is_valid = True
    #     elif self.extension == ".txt":
    #         self.read_txt_data()
    #         is_valid = True
    #     elif self.extension == ".csv":
    #         self.read_csv_data()
    #         is_valid = True
    #     elif self.extension == "":
    #         print("Selected a file with no extension")
    #     else:
    #         print(f"File extension {self.extension} not supported")

    #     return is_valid

    # # TODO: Find a way to run without the need to create tif files
    # def read_lif_data(self) -> None:
    #     lif_file = LifFile(self.full_path)

    #     for i, image in enumerate(lif_file.get_iter_image()):
    #         new_series = Series()
    #         new_series.index = i
    #         new_series.filename = image.filename
    #         new_series.name = image.name
    #         new_series.frames = image.nt
    #         new_series.width_px = image.dims[0]
    #         new_series.height_px = image.dims[1]
    #         new_series.mpp = image.scale[0]
    #         new_series.width_SI = math.floor(
    #             new_series.width_px / image.scale[0])
    #         new_series.height_SI = math.floor(
    #             new_series.height_px / image.scale[1])
    #         new_series.fps = image.scale[-1]
    #         new_series.time_lag = 1 / new_series.fps

    #         self.series.append(new_series)

    #         del new_series

    #     del lif_file

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

    # def read_avi_data(self) -> None:
    #     print("avi file selected")
    #     # print("Loading only luminance channel")
    #     # avi_video = skvideo.io.vread(
    #     #     self.full_path, outputdict={"-pix_fmt": "gray"})[:, :, :, 0]

    #     # print(skvideo.io.avprobe(self.full_path))
    #     # print(skvideo.io.mprobe(self.full_path))
    #     avi_file = skvideo.io.ffprobe(self.full_path)

    #     new_series = Series()

    #     new_series.name = self.file_name
    #     new_series.frames = int(avi_file['video']['@nb_frames'])
    #     new_series.width_px = int(avi_file['video']['@width'])
    #     new_series.height_px = int(avi_file['video']['@height'])
    #     new_series.width_SI = None
    #     new_series.height_SI = None
    #     duration = float(avi_file['video']['@duration'])
    #     new_series.fps = new_series.frames / duration
    #     new_series.time_lag = 1 / new_series.fps

    #     self.series.append(new_series)

    #     del new_series, avi_file

    # def read_txt_data(self) -> None:
    #     print("txt file selected")
    #     raw_data = self.import_txt()
    #     raw_data = self.clean_data(raw_data)
    #     raw_data = self.correct_separator(raw_data)
    #     raw_data = self.remove_index(raw_data)
    #     # data['particle'] = 0
    #     data_list = self.split_trajectories(raw_data)
    #     for data in data_list:
    #         data = self.add_trajectory_nr(data)
    #     data_list = self.get_valid_trajectories(data_list)
    #     for data in data_list:
    #         data = self.to_numeric(data)

    #     self.trajectories = pd.concat(data_list)
    #     print(self.trajectories.head())

    # def to_numeric(self, data):
    #     data["particle"] = pd.to_numeric(data["particle"])
    #     data["frame"] = pd.to_numeric(data["frame"])
    #     data["x"] = pd.to_numeric(data["x"])
    #     data["y"] = pd.to_numeric(data["y"])
    #     return data

    # def get_valid_trajectories(self, data):
    #     result = []
    #     for trajectory in data:
    #         if len(trajectory) >= 590:
    #             result.append(trajectory)

    #     return result

    # def add_trajectory_nr(self, data):
    #     if len(data) > 0:
    #         data.reset_index(drop=True, inplace=True)
    #         data.insert(loc=0, column='particle', value=data.at[0, 'y'])
    #         # data['particle'] = data.at[0,'y']
    #         data.drop([0], inplace=True)

    #     return data

    # def split_trajectories(self, data):
    #     result = []
    #     last_index = 0
    #     for ind, column in data.iterrows():
    #         if data.loc[ind, "x"] == 0:
    #             index = ind
    #             result.append(data.iloc[last_index:index])
    #             last_index = ind

    #     result.append(data.iloc[last_index:index])

    #     return result

    # def remove_index(self, data):
    #     data.reset_index(drop=True, inplace=True)
    #     return data

    # def correct_separator(self, data):
    #     data.replace(to_replace=",", value=".",
    #                  regex=True, inplace=True)
    #     return data

    # def clean_data(self, data):
    #     data.loc[:, "x"].replace(
    #         to_replace="Trajectory", value=0, regex=True, inplace=True
    #     )

    #     # Delete rows that have the value 'frame'
    #     indexNames = data[data['x'] == 'frame'].index
    #     data.drop(indexNames, inplace=True)

    #     return data

    # def import_txt(self) -> pd.DataFrame:

    #     f = open(self.full_path)
    #     f_list = list(f)
    #     first_trajectory_row = f_list.index('%% Trajectory 1\n')
    #     f.close()

    #     rows_to_skip = first_trajectory_row + 1

    #     data = pd.read_csv(
    #         self.full_path,
    #         skiprows=rows_to_skip,
    #         delim_whitespace=True,
    #         usecols=[0, 1, 2],
    #         names=["frame", "x", "y"],
    #         # decimal=",",
    #     )
    #     return data

    # def read_csv_data(self) -> None:
    #     print("csv file selected")
    #     # csv_file = pd.read_csv(self.full_path, usecols=[0, 1])

    #     new_series = Series()

    #     new_series.name = self.file_name
    #     new_series.frames = None
    #     new_series.width_px = None
    #     new_series.height_px = None
    #     new_series.width_SI = None
    #     new_series.height_SI = None
    #     new_series.fps = None
    #     new_series.time_lag = None

    #     self.series.append(new_series)

    #     # del new_series, csv_file
    #     del new_series

    # def analyze(self) -> None:
    #     # ============================ Locate features in all frames
    #     print(f"\nLocating particles in all frames...")
    #     self.features = tp.batch(
    #         self.frames[:], self.f_size, minmass=self.m_mass)
    #     # ============================ Link features into particle trajectories
    #     print("Linking particles into trajectories...")
    #     all_trajectories = tp.link(self.features, self.f_size, memory=0)

    #     # ============================ Filter spurious trajectories
    #     print("Filtering trajectories...")
    #     self.trajectories = tp.filter_stubs(all_trajectories, self.filter)

    #     # Compare the number of particles in the unfiltered and filtered data.
    #     print(f"Before: {all_trajectories['particle'].nunique()}")
    #     print(f"After: \t{self.trajectories['particle'].nunique()}")

    # def refine(self) -> None:
    #     # Convenience function -- just plots size vs. mass
    #     tp.mass_size(self.trajectories.groupby('particle').mean())

    #     # mass: brightness of the particle
    #     # size: diameter of the particle
    #     # ecc: eccentricity of the particle (0 = circular)
    #     t2 = self.trajectories[(
    #         (self.trajectories['mass'] > self.m_mass) &
    #         (self.trajectories['size'] < self.m_size) &
    #         (self.trajectories['ecc'] < self.m_ecc))]

    #     tp.annotate(t2[t2['frame'] == 0], self.frames[0])

    #     # ax = tp.plot_traj(t2)
    #     # plt.show()

    #     # ============================== Remove overall drift
    #     print("Removing drift...")
    #     drift = tp.compute_drift(t2)
    #     drift.plot()
    #     plt.show()

    #     self.trajectories = tp.subtract_drift(t2.copy(), drift)
    #     ax = tp.plot_traj(self.trajectories)
    #     plt.show()

    # def analyze_trajectories(self) -> None:
    #     # ============================== Analyze trajectories
    #     print("Analyzing trajectories...")
    #     self.mlt = math.ceil(self.fps*10)  # Time to use (10s, 1s, 0.1s)

    #     self.msd = tp.imsd(self.trajectories, self.mpp, self.fps, self.mlt)

    #     fig, ax = plt.subplots()
    #     # black lines, semitransparent
    #     ax.plot(self.msd.index, self.msd, 'k-', alpha=0.1)
    #     ax.set(ylabel=r'MSD [$\mu$m$^2$]', xlabel='Timescale ($\\tau$) [$s$]')
    #     ax.set_xscale('log')
    #     ax.set_yscale('log')

    # def get_MSD(self):
    #     self.msd.name = "MSD"
    #     self.msd.index.name = f'Timescale ({chr(120591)}) (s)'

    # def get_EMSD(self):
    #     # ============================== Ensemble Mean Squared Displacement

    #     # In case fps changes between '.tif' files
    #     self.msd['mean'] = self.msd.mean(axis=1)

    #     # Best option ?
    #     em = tp.emsd(self.trajectories, self.mpp, self.fps, self.mlt)
    #     self.msd['mean2'] = em.values

    #     fig, ax = plt.subplots()
    #     ax.plot(self.msd['mean'].index, self.msd['mean'], 'o')
    #     ax.set_xscale('log')
    #     ax.set_yscale('log')
    #     ax.set(ylabel=f'MSD {chr(956)}m{chr(178)}',
    #            xlabel='Timescale ($\\tau$) [$s$]')

    #     plt.figure()
    #     plt.title('Ensemble Data - <MSD> vs. Time Scale')
    #     plt.ylabel(f'MSD {chr(956)}m{chr(178)}')
    #     plt.xlabel('Timescale ($\\tau$) [$s$]')
    #     tp.utils.fit_powerlaw(self.msd['mean'])
    #     # print(f"n: {n}, A: {A}")

    # def get_Deff(self):
    #     self.deff = self.msd.div((4*self.msd.index), axis=0)
    #     self.deff.name = "Deff"

    # def rename_columns(self, data):
    #     columns_names = pd.Series(range(1, len(data.columns)+1))-1
    #     columns_names = [
    #         f'{data.name} {x+1} ({chr(956)}m{chr(178)})' for x in columns_names]
    #     columns_names[len(columns_names) -
    #                   1] = f'<{data.name}> ({chr(956)}m{chr(178)})'
    #     data.columns = columns_names

    #     return data

    # def locate_particles(self):
    #     print("Locating particles...")
    #     self.features = tp.locate(self.frames[0], self.f_size)

    #     # tp.annotate(f, self.frames[0])

    #     # ============================== Refine parameters
    #     print("Refining parameters...")
    #     self.m_mass = math.ceil(self.features.mass.mean())
    #     self.m_size = math.floor(self.features.size.mean())
    #     self.m_ecc = self.features.ecc.mean()

    #     # ============================== Relocate features according to mass
    #     print(f"Relocating particles...\n")
    #     self.features = tp.locate(
    #         self.frames[0], self.f_size, minmass=self.m_mass)

    # def read_tif_file(self):
    #     return pims.open(self.full_path)

    # def analyze_imageJ_report(self):
    #     pass
