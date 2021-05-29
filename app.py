import os
import sys
import time
import datetime
import locale
import pandas as pd
from PySide6.QtGui import QFont
from PySide6.QtCore import QRunnable, Signal, Slot, QThreadPool, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout, QWidget, QMessageBox,
    QDialog, QFileDialog, QCheckBox, QTableWidgetItem,  QTreeWidgetItem
)

# import resources_rc
import mpt
# from mpt.model import Analysis
# from mpt.settings import Settings
from ui.MainWindow import Ui_MainWindow


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread.
    Supplied args and kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @ Slot()  # QtCore.Slot
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        self.fn(*self.args, **self.kwargs)


class ApplicationConfiguration(QDialog):

    update_application = Signal(pd.DataFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()
        self.dialog = loader.load("ui/app_config.ui", self)
        self.connectSignalsSlots()

    def load_app_config(self, config):
        self.config = config
        self.dialog.txt_size.setText(f"{int(config['p_size'])}")
        self.dialog.txt_delta.setText(f"{config['delta_t']:.2f}")
        self.dialog.txt_width_px.setText(f"{int(config['width_px'])}")
        self.dialog.txt_time.setText(f"{config['time']:.2f}")
        self.dialog.txt_filter.setText(f"{int(config['min_frames'])}")
        self.dialog.txt_total_frames.setText(f"{int(config['total_frames'])}")
        self.dialog.txt_width_si.setText(f"{config['width_si']:.2f}")
        self.dialog.txt_temperature_C.setText(f"{config['temperature_C']:.2f}")

    def connectSignalsSlots(self):
        self.dialog.txt_size.textChanged.connect(self.size_changed)
        self.dialog.txt_delta.textChanged.connect(self.delta_changed)
        self.dialog.txt_width_px.textChanged.connect(self.width_px_changed)
        self.dialog.txt_time.textChanged.connect(self.time_changed)
        self.dialog.txt_filter.textChanged.connect(self.filter_changed)
        self.dialog.txt_total_frames.textChanged.connect(
            self.total_frames_changed)
        self.dialog.txt_width_si.textChanged.connect(self.width_si_changed)
        self.dialog.txt_temperature_C.textChanged.connect(
            self.temperature_changed)

        self.dialog.accepted.connect(self.save_values)

    def size_changed(self, text):
        self.config['p_size'] = int(text)

    def delta_changed(self, text):
        self.config['delta_t'] = float(text)
        self.config['fps'] = round(1/(float(text)/1000))

    def width_px_changed(self, text):
        self.config['width_px'] = int(text)

    def time_changed(self, text):
        self.config['time'] = float(text)

    def filter_changed(self, text):
        self.config['min_frames'] = int(text)

    def total_frames_changed(self, text):
        self.config['total_frames'] = int(text)

    def width_si_changed(self, text):
        self.config['width_si'] = float(text)

    def temperature_changed(self, text):
        self.config['temperature_C'] = float(text)

    def save_values(self):
        self.update_application.emit(self.config)


class DiffusivityRanges(QDialog):

    update_diffusivity = Signal(pd.DataFrame)

    def __init__(self, parent=None):
        super().__init__(parent)
        loader = QUiLoader()
        self.dialog = loader.load("ui/diffusivity.ui", self)
        self.connectSignalsSlots()

    def load_diffusivity_config(self, config):
        self.config = config
        self.dialog.txt_active_min.setText(f"{config['active'][0]}")
        self.dialog.txt_diffusive_min.setText(f"{config['diffusive'][0]}")
        self.dialog.txt_subdiffusive_min.setText(
            f"{config['sub_diffusive'][0]}")

    def connectSignalsSlots(self):
        self.dialog.txt_subdiffusive_min.textChanged.connect(
            self.subdiffusive_changed)
        self.dialog.txt_diffusive_min.textChanged.connect(
            self.diffusive_changed)
        self.dialog.txt_active_min.textChanged.connect(
            self.active_changed)
        self.dialog.buttonBox.accepted.connect(self.save_changes)

    def subdiffusive_changed(self, text):
        sub_diffusive_min = float(text)
        self.config['sub_diffusive'][0] = sub_diffusive_min
        self.config['immobile'][1] = sub_diffusive_min - 0.001
        self.dialog.txt_immobile_max.setText(f"{self.config['immobile'][1]}")

    def diffusive_changed(self, text):
        diffusive_min = float(text)
        self.config['diffusive'][0] = diffusive_min
        self.config['sub_diffusive'][1] = diffusive_min - 0.001
        self.dialog.txt_subdiffusive_max.setText(
            f"{self.config['sub_diffusive'][1]}")

    def active_changed(self, text):
        active_min = float(text)
        self.config['active'][0] = active_min
        self.config['diffusive'][1] = active_min - 0.001
        self.dialog.txt_diffusive_max.setText(f"{self.config['diffusive'][1]}")

    def save_changes(self):
        self.update_diffusivity.emit(self.config)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.threadpool = QThreadPool()

        self.setupUi(self)
        self.connectSignalsSlots()

        self.appName = "NPT Hub"
        self.setWindowTitle(
            f"{self.appName} - Multiple Particle Tracking Analysis")

        # settings = Settings()
        self.summary_is_outdated = False
        self.load_project_setup()
        self.load_ui_setup()

    def load_ui_setup(self) -> None:
        # ------------------------------------------------------- General setup
        self.toolBar.setMovable(False)

        # -------------------------------------------------------- Table Widget
        self.summary_view.setColumnWidth(0, 43)
        self.summary_view.setColumnWidth(1, 678)
        self.summary_view.setHorizontalHeaderLabels([
            '', 'File name', 'Trajectories', 'Valid trajectories'])

        # ------------------------------------------------------- Summary total
        self.summary_total.setColumnWidth(0, 721)
        total_font = QFont()
        total_font.setBold(True)
        self.total = QTreeWidgetItem(self.summary_total)
        self.total.setText(0, 'Total')
        self.total.setText(1, str(0))
        self.total.setText(2, str(0))
        self.total.setFont(0, total_font)
        self.total.setFont(1, total_font)
        self.total.setFont(2, total_font)
        self.total.setTextAlignment(0, Qt.AlignRight)
        self.total.setTextAlignment(1, Qt.AlignRight)
        self.total.setTextAlignment(2, Qt.AlignRight)
        self.lock_actions()

    def lock_actions(self):
        self.actionRemove_selected.setEnabled(False)
        self.actionStart_analysis.setEnabled(False)
        self.actionStart_analysis_tp.setEnabled(False)
        self.actionClear_summary.setEnabled(False)
        self.actionExport_files.setEnabled(False)

    def unlock_actions(self):
        self.actionRemove_selected.setEnabled(True)
        self.actionStart_analysis.setEnabled(True)
        self.actionStart_analysis_tp.setEnabled(True)
        self.actionClear_summary.setEnabled(True)
        self.actionExport_files.setEnabled(True)

    def load_project_setup(self) -> None:
        locale.setlocale(locale.LC_ALL, '')
        self.analysis = mpt.analysis
        self.diffusivity = mpt.diffusivity
        self.general = mpt.general

    def connectSignalsSlots(self):
        self.actionImport_files.triggered.connect(self.on_import_files)
        self.actionRemove_selected.triggered.connect(self.on_remove_selected)
        self.actionClear_summary.triggered.connect(self.on_clear_summary)
        self.actionStart_analysis.triggered.connect(self.on_start_analysis)
        self.actionStart_analysis_tp.triggered.connect(
            self.on_start_analysis_tp)
        self.actionExport_files.triggered.connect(self.on_export_files)
        self.actionAbout.triggered.connect(self.on_about)
        self.actionExit.triggered.connect(self.close)

        self.actionApplication_configuration.triggered.connect(
            self.on_application_configuration)
        self.actionDiffusivity_ranges.triggered.connect(
            self.on_diffusivity_ranges)

    def show_message(self, message, timeout=2500):
        self.statusbar.showMessage(message, timeout)

    def on_import_files(self):
        self.show_message("Import ImageJ files")
        self.get_summary()

        if self.analysis.summary.empty:
            return

        self.update_summary_view()

        self.actionRemove_selected.setEnabled(True)
        self.actionStart_analysis.setEnabled(True)
        self.actionStart_analysis_tp.setEnabled(True)
        self.actionClear_summary.setEnabled(True)

    def on_remove_selected(self):
        items_to_remove = []
        for row in range(self.summary_view.rowCount()):
            if self.summary_view.cellWidget(row, 0).children()[1].isChecked():
                items_to_remove.append(row)

        self.remove_summary_items(items_to_remove)

    def on_clear_summary(self):
        self.show_message("Starting summary clear...")
        self.analysis.clear_summary()
        self.summary_view.setRowCount(0)
        self.update_totals()

        self.actionRemove_selected.setEnabled(False)
        self.actionStart_analysis.setEnabled(False)
        self.actionStart_analysis_tp.setEnabled(False)
        self.actionClear_summary.setEnabled(False)
        self.actionExport_files.setEnabled(False)
        self.show_message("Summary cleared")

    def on_start_analysis(self):
        worker = Worker(self.mpt_analysis)
        self.threadpool.start(worker)

    def on_start_analysis_tp(self):
        worker = Worker(self.mpt_analysis_tp)
        self.threadpool.start(worker)

    def on_export_files(self):
        selected_folder = QFileDialog.getExistingDirectory(
            parent=self, caption='Chose folder to save report files',
            dir=self.general.config.save_folder)

        if not selected_folder:
            self.show_message("Canceling report saving....")
            return None

        self.general.config.save_folder = os.path.abspath(selected_folder)
        self.general.update()
        self.show_message(
            f"Saving reports to {self.general.config.save_folder}...")

        worker = Worker(self.export_reports)
        self.threadpool.start(worker)
        # self.export_reports()

    def on_about(self):
        QMessageBox.about(
            self,
            f"About {self.appName}",
            f"<p>{self.appName} is a software developed for "
            "nanoparticle analysis with potential to include more functions "
            "in the future.</p>"
            "<p>It is available as a Free and Open Source application to allow"
            "researh growth.</p>"
            "<p>It uses several well known Python packages, such as:</p>"
            "<ul>- PyQt</ul>"
            "<ul>- Qt Designer</ul>"
            "<ul>- Pandas</ul>"
            "<ul>- Numpy</ul>"
            "<ul>- Matplotlib</ul>",
        )

    def on_application_configuration(self):
        self.application_dialog = ApplicationConfiguration(self)
        self.application_dialog.load_app_config(
            self.analysis.config.copy())

        self.application_dialog.update_application.connect(
            self.update_app_config)
        self.application_dialog.dialog.buttonBox.rejected.connect(
            self.discard_config_changes)

        self.application_dialog.dialog.show()

    def on_diffusivity_ranges(self):
        self.diffusivity_dialog = DiffusivityRanges()
        self.diffusivity_dialog.load_diffusivity_config(
            self.diffusivity.config.copy())

        self.diffusivity_dialog.update_diffusivity.connect(
            self.update_diffusivity_config)
        self.diffusivity_dialog.dialog.buttonBox.rejected.connect(
            self.discard_config_changes)

        self.diffusivity_dialog.dialog.show()

    def get_summary(self):

        file_list, _ = QFileDialog.getOpenFileNames(
            parent=self, caption='Open ImageJ Full report file(s)',
            dir=self.general.config.open_folder,
            filter="ImageJ full report files (*.csv)")

        start_time = time.time()

        if not file_list:
            self.show_message("No file selected...")
            return None

        part_time = time.time()
        self.show_message("File(s) selected...")

        self.analysis.load_reports(file_list)
        print(time.time() - part_time)

        self.show_message("Filtering valid trajectories...")
        self.analysis.get_valid_trajectories()

        self.show_message("Creating summary...")
        self.analysis.summarize()

        self.general.config.open_folder = os.path.dirname(file_list[0])
        self.general.update()

        execution_time = (time.time() - start_time)

        if execution_time > 60:
            execution_time_min = int(execution_time/60)
            execution_time_sec = execution_time - 60 * execution_time_min
            elapsed_time_formatted = (
                f"{execution_time_min} min, {execution_time_sec:.2f} s")
        else:
            elapsed_time_formatted = f"{execution_time:.2f} s"

        elapsed_time_message = f"Elapsed time: {elapsed_time_formatted}"
        self.show_message(f"Data fetched! {elapsed_time_message}", 5000)

    def update_summary_view(self):
        self.summary_view.clearContents()
        self.summary_view.setRowCount(len(self.analysis.summary))

        for index, report in self.analysis.summary.iterrows():
            remove_widget = QWidget()
            remove = QCheckBox()
            remove.setChecked(False)
            remove_layout = QHBoxLayout(remove_widget)
            remove_layout.addWidget(remove)
            remove_layout.setAlignment(Qt.AlignCenter)
            remove_layout.setContentsMargins(0, 0, 0, 0)
            remove_widget.setLayout(remove_layout)
            self.summary_view.setCellWidget(index, 0, remove_widget)

            self.summary_view.setItem(
                index, 1,
                QTableWidgetItem(report.file_name))
            self.summary_view.setItem(
                index, 2,
                QTableWidgetItem(str(report.trajectories)))
            self.summary_view.setItem(
                index, 3,
                QTableWidgetItem(str(report.valid)))
            self.summary_view.item(
                index, 2).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
            self.summary_view.item(
                index, 3).setTextAlignment(Qt.AlignCenter | Qt.AlignRight)

        self.update_totals()

    def update_totals(self):
        if self.analysis.summary.empty:
            summary_total = {'trajectories': 0, 'valid': 0}
        else:
            summary_total = self.analysis.summary.iloc[:, 1:].sum()

        self.total.setText(1, str(summary_total['trajectories']))
        self.total.setText(2, str(summary_total['valid']))

    def remove_summary_items(self, rows):
        for row in rows:
            self.analysis.remove_file_trajectories(
                self.summary_view.item(row, 1).data(0))

        self.update_summary_view()
        self.actionRemove_selected.setDisabled(self.analysis.summary.empty)

    def mpt_analysis(self):
        self.actionImport_files.setEnabled(False)
        self.lock_actions()
        self.show_message(
            "Computing MSD (mean squared displacement)...")

        self.setCursor(Qt.BusyCursor)

        startTime = time.time()

        self.show_message("Starting trajectory analysis...")
        self.analysis.compute_msd()
        self.analysis.compute_msd_log()

        self.show_message(
            "Computing Deff (diffusivity coefficient)...")
        self.analysis.compute_deff()

        self.show_message(
            "Adjusting data labels...")

        self.analysis.msd = self.analysis.rename_columns(
            self.analysis.msd, "MSD")
        self.analysis.msd_log = self.analysis.rename_columns(
            self.analysis.msd_log, "MSD-LOG")
        self.analysis.deff = self.analysis.rename_columns(
            self.analysis.deff, "Deff")
        executionTime = (time.time() - startTime)

        self.setCursor(Qt.ArrowCursor)
        self.actionExport_files.setDisabled(self.analysis.msd.empty)

        elapsed_time_message = f"Elapsed time: {executionTime:.2f}"
        self.show_message(
            f"Trajectory analysis complete... {elapsed_time_message}")
        self.unlock_actions()
        self.actionImport_files.setEnabled(True)

    def mpt_analysis_tp(self):
        self.show_message("Starting trajectory analysis...")
        self.setCursor(Qt.BusyCursor)

        startTime = time.time()
        self.analysis.start_trackpy()
        executionTime = (time.time() - startTime)

        self.setCursor(Qt.ArrowCursor)
        self.actionExport_files.setDisabled(self.analysis.msd.empty)

        elapsed_time_message = f"Elapsed time: {executionTime:.2f}"
        self.show_message(
            f"Trajectory analysis complete... {elapsed_time_message}")

    def export_reports(self):
        self.show_message(
            f"Saving reports to {self.general.config.save_folder}...")

        startTime = time.time()
        self.analysis.export(self)
        executionTime = (time.time() - startTime)

        elapsed_time_message = f"Elapsed time: {executionTime:.2f}"
        self.show_message(f"Reports saved. {elapsed_time_message}")

    @Slot(pd.DataFrame)
    def update_diffusivity_config(self, config):
        self.show_message("Saving changes...")
        self.diffusivity.config = config
        self.diffusivity.update()

    @Slot(pd.DataFrame)
    def update_app_config(self, config):
        self.show_message("Saving changes...")
        if self.analysis.config != config:
            self.analysis.config = config
            self.analysis.update()

            # current_filter = int(self.analysis.config['min_frames'])
            # new_filter = int(config['min_frames'])
            # if current_filter == new_filter:
            #     self.update_summary_view()

    def discard_config_changes(self):
        self.show_message("Discarding changes...")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
