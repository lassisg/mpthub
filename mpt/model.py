import mpt.database as db
import pandas as pd
import os


class General():

    def __init__(self) -> None:
        print("Initializing General app configuration object...")

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
        print("Initializing Diffusivity configuration object...")

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
        print("Initializing Analysis configuration object...")
        self.summary = pd.DataFrame()

    def load_config(self) -> None:
        """Loads configuration into a Series with data from database.
        """
        conn = db.connect()
        config_df = pd.read_sql_table("analysis_config", con=conn)
        self.config = config_df.iloc[0]

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

    def load_reports(self, file_list: list) -> None:
        """Loads '.csv' files into DB table 'trajectories' after filtering \
            by valid trajectories.

        Arguments:
            file_list {list} -- File path list to be imported.
        """
        self.trajectories = pd.DataFrame()
        print("Loading reports")
        for file in file_list:
            # TODO: Check if new data exists before add
            if not self.summary.empty:
                masked_df = self.summary.full_path == file
                if masked_df.any():
                    continue

            full_data = pd.read_csv(file)
            if set(['Trajectory', 'Frame', 'x', 'y']).issubset(
                    full_data.columns):
                print("File ok!")
                raw_data = full_data.loc[:, ['Trajectory', 'Frame', 'x', 'y']]

                full_path = file
                file_name, _ = os.path.splitext(os.path.basename(file))
                trajectories = len(
                    raw_data.iloc[:, :1].groupby('Trajectory').nunique())
                valid = self.get_valid_trajectories(raw_data)

                self.summary = self.summary.append({
                    'full_path': full_path, 'file_name': file_name,
                    'trajectories': trajectories, 'valid': valid},
                    ignore_index=True)
            else:
                print(f"Wrong file format. Aborting import of file: '{file}'")

            # report_list.append(new_report)

            # del new_report

    def get_valid_trajectories(self, data_in: pd.DataFrame) -> int:
        print("Filter valid trajectories")
        grouped_trajectories = data_in.groupby('Trajectory').filter(
            lambda x: len(x['Trajectory']) > self.config.min_frames)

        valid_trajectories = grouped_trajectories.iloc[:, :1].groupby(
            'Trajectory').nunique()

        # for trajectory in self.valid_trajectories_number:
        #     self.valid_trajectories_list.append(
        #         grouped_trajectories.
        #         loc[grouped_trajectories['Trajectory'] == trajectory].
        #         reset_index(drop=True))

        # self.valid_trajectories = len(self.valid_trajectories_number)
        return len(valid_trajectories)


class Results():
    pass
