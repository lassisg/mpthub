import mpt.database as db
import pandas as pd
import os


class General():

    def __init__(self) -> None:
        # print("Initializing General app configuration object...")
        self.load_config()

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
        # print("Initializing Diffusivity configuration object...")
        self.load_config()

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
        # print("Initializing Analysis configuration object...")
        self.summary = pd.DataFrame()
        self.load_config()

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

    def load_reports(self, parent, file_list: list) -> None:
        """Loads '.csv' files into DB table 'trajectories' after filtering \
            by valid trajectories.

        Arguments:
            file_list {list} -- File path list to be imported.
        """
        self.trajectories = pd.DataFrame(
            columns=['file_name', 'Trajectory', 'Frame', 'x', 'y'])
        parent.statusBar.SetStatusText("Loading report(s)...")
        for file in file_list:
            if not self.summary.empty:
                masked_df = self.summary.full_path == file
                if masked_df.any():
                    continue

            full_data = pd.read_csv(file)
            file_name, _ = os.path.splitext(os.path.basename(file))
            if set(['Trajectory', 'Frame', 'x', 'y']).issubset(
                    full_data.columns):
                parent.statusBar.SetStatusText(f"File {file_name} ok!")
                raw_data = full_data.loc[:, ['Trajectory', 'Frame', 'x', 'y']]

                full_path = file

                parent.statusBar.SetStatusText(
                    f"Importing file {file_name}...")
                trajectories = len(
                    raw_data.iloc[:, :1].groupby('Trajectory').nunique())
                valid = self.get_valid_trajectories(
                    parent, file_name, raw_data)

                self.summary = self.summary.append({
                    'full_path': full_path, 'file_name': file_name,
                    'trajectories': trajectories, 'valid': valid},
                    ignore_index=True)
            else:
                parent.statusBar.SetStatusText(f"Wrong file format.")
                parent.statusBar.SetStatusText(
                    f"Aborting import of file: '{file_name}'")

        if not self.trajectories.empty:
            self.add_trajectories(self.trajectories)

    def add_trajectories(self, data):
        conn = db.connect()
        data.to_sql('trajectories', con=conn,
                    index=False, if_exists='replace')

    def clear_trajectories(self) -> None:
        conn = db.connect()
        empty_data = pd.DataFrame(
            columns=['file_name', 'Trajectory', 'Frame', 'x', 'y'])
        empty_data.to_sql('trajectories', con=conn,
                          index=False, if_exists='replace')

    def get_valid_trajectories(self, parent,
                               file_name: str,
                               data_in: pd.DataFrame) -> int:
        parent.statusBar.SetStatusText(
            f"Filtering valid trajectories on {file_name}...")
        grouped_trajectories = data_in.groupby('Trajectory').filter(
            lambda x: len(x['Trajectory']) > self.config.min_frames)

        valid_trajectories = grouped_trajectories.iloc[:, :1].groupby(
            'Trajectory').nunique()

        valid_trajectories_data = data_in[data_in['Trajectory'].isin(
            valid_trajectories.iloc[:, 0].index.values)]
        valid_trajectories_data.insert(0, 'file_name', file_name)
        self.trajectories = self.trajectories.append(
            valid_trajectories_data, ignore_index=True)

        return len(valid_trajectories)


class Results():
    pass
