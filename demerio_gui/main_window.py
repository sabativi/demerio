from demerio_sync.storage_manager import StorageManager
from demerio_sync.dropbox_api import DropboxAPI
from demerio_sync.box_api import BoxAPI
from demerio_sync.google_drive_api import GoogleDriveAPI
from demerio_daemon.observer import Observer
from demerio_daemon.daemon import DemerioDaemon
from demerio_mapping.mapping_config_parser import MappingConfigParser as Mapping
from demerio_split.fec import FileFec
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QUrl
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QListView
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QCoreApplication
from resources.demerio_qrc import *
from system_tray import SystemTray
from cloud_widget import CloudWidget
from demerio_conductor.demerio_conductor import DemerioConductor
from version import get_versions
from params import *


class MainWindow(QDialog):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = uic.loadUi(ui_full_path('main_window.ui'), self)
        self.ui.label_version.setText("Demerio version %s" % (get_versions()['version'],))
        self.ui.start_btn.setVisible(False)
        self.ui.progress_bar.setVisible(False)
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.launch_btn.clicked.connect(self.launch_daemon)
        self.ui.output_btn.clicked.connect(self.validate)
        self.ui.start_btn.clicked.connect(self.reconstruct_data)
        self.tray = SystemTray(self)
        self.tray.show()
        self.create_tray_actions()
        self.init_storage_manager()
        self.add_clouds_to_view()
        self.daemon = None

    def create_tray_actions(self):
        self.tray.add_action("Open Demerio Folder", self.open_demerio_folder)
        self.tray.add_action("Preference", self.show)
        self.tray.add_separator()
        self.tray.add_action("Quit", self.quit_app)

    """
    should be done in cloud widget class with a proper model and view
    """
    def init_storage_manager(self):
        self.storage_manager = StorageManager()
        drive_api = GoogleDriveAPI(demerio_config_dir)
        self.storage_manager.add_storage("google_drive", drive_api)
        dropbox = DropboxAPI(demerio_config_dir)
        self.storage_manager.add_storage("dropbox", dropbox)
        box = BoxAPI(demerio_config_dir)
        self.storage_manager.add_storage("box", box)

    def add_clouds_to_view(self):
        self.ui.listWidget.setResizeMode(QListView.Adjust)
        for cloud_name in self.storage_manager.map_of_storage.keys():
            cloud_widget = CloudWidget(cloud_name, self)
            cloud_widget.pushed.connect(self.authenticate)
            item = QListWidgetItem()
            item.setSizeHint(cloud_widget.sizeHint())
            self.ui.listWidget.addItem(item)
            self.ui.listWidget.setItemWidget(item, cloud_widget)

    @pyqtSlot()
    def authenticate(self):
        cloud_storage = self.storage_manager.map_of_storage[self.sender().name]
        cloud_storage.authorize()
        if cloud_storage.is_connected():
            self.sender().ui.cloudAction.setEnabled(False)
        self.update_launch_btn_state()

    @pyqtSlot()
    def open_demerio_folder(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(demerio_dir))

    def update_launch_btn_state(self):
        for cloud in self.storage_manager.map_of_storage.values():
            if not cloud.is_connected():
                return False
        self.ui.launch_btn.setEnabled(True)
        self.ui.label.setText("")

    @pyqtSlot()
    def launch_daemon(self):
        self.ui.launch_btn.hide()
        self.hide()
        self.ui.account_tab.setEnabled(True)
        number_of_storages = self.storage_manager.get_number_of_storages()
        self.event_handler = DemerioConductor(Mapping(demerio_dir, config_file), FileFec(PARTS_NEEDED, number_of_storages), self.storage_manager)
        self.event_handler.conductor_exception.connect(self.tray.conductor_problem)
        self.event_handler.event_started.connect(self.tray.event_started)
        self.event_handler.event_finished.connect(self.tray.event_finished)
        observer = Observer()
        self.daemon = DemerioDaemon(self.event_handler, observer, demerio_dir, should_exit=False)
        self.daemon.start()
        self.open_demerio_folder()

    @pyqtSlot()
    def validate(self):
        self.dir_selected = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.ui.start_btn.setVisible(True)
        self.ui.progress_bar.setVisible(True)
        self.ui.progress_bar.setMaximum(180)
        self.ui.progress_bar.setTextVisible(True)
        self.ui.start_label.setText("Your datas will be reconstructed in : %s directory" %(self.dir_selected,))

    @pyqtSlot()
    def reconstruct_data(self):
        self.event_handler.reconstruct_dir(self.dir_selected)

    @pyqtSlot()
    def quit_app(self):
        if self.daemon is not None:
            self.daemon.should_exit = True
            self.daemon.join()
        QCoreApplication.instance().quit()

