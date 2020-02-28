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


class MPT_File():
    def __init__(self) -> None:
        self.config_path = None
        self.full_path = None
        self.file_path = None
        self.file_name = None
        self.file_ext = None
        # Ask User in config
        self.frames = 606
        self.width_px = 512
        self.height_px = 512
        self.width_SI = 160
        self.height_SI = 160
        self.fps = 30
        self.f_size = 11
        # Calculate from user input
        self.filter = ceil(self.frames * .975)
        self.mpp = self.width_SI/self.width_px
        self.time_lag = 1 / self.fps

        # self.m_mass = None
        # self.m_size = None
        # self.m_ecc = None
        # self.mlt = 0.0
        # self.features = pd.DataFrame()  # particles
        # self.trajectories = pd.DataFrame()
        # self.msd = pd.DataFrame()
        # self.deff = pd.DataFrame()

    def from_txt(self) -> pd.DataFrame:

        f = open(self.full_path)
        f_list = list(f)
        first_trajectory_row = f_list.index('%% Trajectory 1\n')
        f.close()

        rows_to_skip = first_trajectory_row + 1

        data = pd.read_csv(
            self.full_path,
            skiprows=rows_to_skip,
            delim_whitespace=True,
            usecols=[0, 1, 2],
            names=["frame", "x", "y"],
            # decimal=",",
        )
        return data

    def from_csv(self) -> pd.DataFrame:
        data = pd.read_csv(
            self.full_path,
            skiprows=1,
            usecols=[0, 1, 2, 3],
            names=["particle", "frame", "x", "y"],
            # decimal=",",
        )
        return data

    def from_tif(self) -> pd.DataFrame:
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
        features = tp.batch(frames[:], self.f_size, minmass=self.m_mass)
        # processes="auto")

        # ============================ Link features into particle trajectories
        print("Linking particles into trajectories...")
        data = tp.link(features, self.f_size, memory=0)

        return data

    def from_avi(self) -> pd.DataFrame:
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

    # TODO: Find a way to run without the need to create tif files
    def get_lif_metadata(self) -> None:
        lif_file = LifFile(self.full_path)

        for i, image in enumerate(lif_file.get_iter_image()):
            new_series = Series()
            new_series.index = i
            new_series.filename = image.filename
            new_series.name = image.name
            new_series.frames = image.nt
            new_series.width_px = image.dims[0]
            new_series.height_px = image.dims[1]
            new_series.mpp = image.scale[0]
            new_series.width_SI = math.floor(
                new_series.width_px / image.scale[0])
            new_series.height_SI = math.floor(
                new_series.height_px / image.scale[1])
            new_series.fps = image.scale[-1]
            new_series.time_lag = 1 / new_series.fps

        del lif_file

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

        del tif_file

    # def get_avi_metadata(self) -> None:
    #     # print("avi file selected")
    #     # print("Loading only luminance channel")
    #     # avi_video = skvideo.io.vread(
    #     #     self.full_path, outputdict={"-pix_fmt": "gray"})[:, :, :, 0]

    #     # print(skvideo.io.avprobe(self.full_path))
    #     # print(skvideo.io.mprobe(self.full_path))
    #     avi_file = skvideo.io.ffprobe(self.full_path)

    #     self.frames = int(avi_file['video']['@nb_frames'])
    #     self.width_px = int(avi_file['video']['@width'])
    #     self.height_px = int(avi_file['video']['@height'])
    #     self.width_SI = None
    #     self.height_SI = None
    #     duration = float(avi_file['video']['@duration'])
    #     self.fps = round(self.frames / duration)
    #     self.time_lag = 1 / self.fps

    #     del avi_file

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
