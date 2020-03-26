import mpt.database as db
import pandas as pd


class Diffusivity:

    def __init__(self) -> None:
        self.config = self.load_config()

    def load_config(self) -> dict:
        # TODO: Load config from db
        return {
            'immobile': {'min': 0, 'max': 0.199},
            'sub_diffusive': {'min': 0.201, 'max': 0.899},
            'diffusive': {'min': 0.901, 'max': 1.199},
            'active': {'min': 1.201}
        }

    def update(self, new_config: dict) -> None:
        # TODO: Update table in db
        for pid, config in new_config.items():
            print(pid)
            for key, value in config.items():
                print(f"{key}: {value}")


class Analysis():

    def __init__(self) -> None:
        self.config = self.load_config()
        print("OK")

    def load_config(self) -> pd.Series:
        conn = db.connect()
        config_df = pd.read_sql_table("analysis_config", con=conn)
        config = config_df.iloc[0]
        return config

    def update(self, new_config: pd.Series) -> None:
        conn = db.connect()
        test = new_config.to_frame(0).T
        test.to_sql('analysis_config', con=conn,
                    index=False, if_exists='replace')
