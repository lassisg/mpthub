import xlsxwriter


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
