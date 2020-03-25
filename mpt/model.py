from mpt.database import Database
from dynaconf import settings


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
