import mpt.database as db
import pandas as pd


class Diffusivity:

    def __init__(self) -> None:
        print("Initializing Diffusivity configuration object...")

    def load_config(self) -> pd.DataFrame:
        """Loads configuration and return DataFrame with data from database.

        Returns:
            pd.DataFrame -- Data from diffusivity table.
        """
        conn = db.connect()
        config_df = pd.read_sql_table("diffusivity", con=conn)
        return config_df

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

    def load_config(self) -> pd.Series:
        """Loads configuration and return DataFrame with data from database.

        Returns:
            pd.Series -- Data from analysis_config table.
        """
        conn = db.connect()
        config_df = pd.read_sql_table("analysis_config", con=conn)
        config = config_df.iloc[0]
        return config

    def update(self, new_config: pd.Series) -> None:
        """Updates analysis_config ranges data on database.

        Arguments:
            new_config {pd.Series} -- New data to be updated in \
                analysis_config table.
        """
        conn = db.connect()
        test = new_config.to_frame(0).T
        test.to_sql('analysis_config', con=conn,
                    index=False, if_exists='replace')
