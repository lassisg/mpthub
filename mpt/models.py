import xlsxwriter
import pandas as pd
import mpt.database as db


class ImageJReport():

    def __init__(self, _full_path, _path="", _file_name="") -> None:
        self.full_path = _full_path
        self.path = _path
        self.file_name = _file_name
        self.trajectory_count = 0
        self.valid_trajectory_count = 0

    def update_trajectory_count(self, _new_trajectory_count: int) -> None:
        self.trajectory_count = _new_trajectory_count

    def update_valid_trajectory_count(
            self, _new_valid_trajectory_count: int) -> None:
        self.valid_trajectory_count = _new_valid_trajectory_count

    def save_to_DB(self):
        summary_df = pd.DataFrame({
            'full_path': self.full_path,
            'path': self.path,
            'file_name': self.file_name,
            'trajectory_count': self.trajectory_count,
            'valid_trajectory_count': self.valid_trajectory_count
        })

        conn = db.connect()
        summary_df.to_sql('summary', con=conn, index=False, if_exists='fail')


class Report():

    def __init__(self) -> None:
        self.file_name = None
        self.file_path = None
        self.sheet_list = []


class IndividualReport(Report):

    def __init__(self) -> None:
        super().__init__()


class TransportModeReport(Report):

    def __init__(self) -> None:
        super().__init__()


class EinsteinStokesReport(Report):

    def __init__(self) -> None:
        super().__init__()


class ReportChart(xlsxwriter.chart):

    def __init__(self):
        super().__init__()
        self.sheet = None
        self.type = None
