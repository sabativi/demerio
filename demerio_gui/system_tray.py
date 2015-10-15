from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtWidgets import QWidget
from demerio_conductor.connection_handler import ConnectionHandler
from params import *


def Enum(**enums):
    "Tricks to implement enum"
    return type('Enum', (), enums)

class IconManagement(object):

    def __init__(self, tray, interval = 100):
        self.tray = tray
        self.movie = QMovie(":/images/tray_animations/tray.gif")
        self.movie.setSpeed(interval)
        self.movie.frameChanged.connect(self.next_icon)
        self.icons = Enum(
            ok = QIcon(":/images/demerio.png"),
            problem = QIcon(":/images/demerio-problem.png"),
            conductor_problem = QIcon(":/images/demerio-conductor-problem.png")
        )
        self.icon = self.icons.ok
        self.update_icon()

    def internet_is_ok(self, internet_is_ok):
        self.icon = self.icons.ok if internet_is_ok else self.icons.problem
        self.update_icon()

    @pyqtSlot(int)
    def next_icon(self, i):
        self.tray.setIcon(QIcon(self.movie.currentPixmap()))

    def start(self):
        self.movie.start()

    def stop(self):
        self.update_icon()
        self.movie.stop()

    def update_icon(self):
        self.tray.setIcon(self.icon)

    def conductor_problem(self):
        if self.movie.state() == QMovie.Running:
            self.movie.stop()
        self.icon = self.icons.conductor_problem
        self.update_icon()

class SystemTray(QWidget):

    def __init__(self, parent=None):
        super(SystemTray, self).__init__(parent)
        self.tray_icon_menu = QMenu(self)
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.icon_management = IconManagement(self.tray_icon)
        self.connection_handler = ConnectionHandler(FREQUENCY_CHECK_MS, TIME_OUT_CALL_S, self)
        self.connection_handler.value_changed.connect(self.internet_connection)
        self.connection_handler.start()

    def add_action(self, name, triggered_action):
        action = QAction(QCoreApplication.translate(trad_context, name), self, triggered = triggered_action)
        self.tray_icon_menu.addAction(action)

    def add_separator(self):
        self.tray_icon_menu.addSeparator()

    def show(self):
        super(SystemTray, self).show()
        self.tray_icon.show()

    @pyqtSlot()
    def event_started(self):
        self.icon_management.start()

    @pyqtSlot()
    def event_finished(self):
        self.icon_management.stop()

    @pyqtSlot(Exception)
    def conductor_problem(self, e):
        self.notify("Demerio", "There was a problem : %s" % (e,))
        self.icon_management.conductor_problem()

    @pyqtSlot(bool)
    def internet_connection(self, internet_is_ok):
        if not internet_is_ok:
            self.notify("Demerio", "Internet connection is lost")
        self.icon_management.internet_is_ok(internet_is_ok)

    def notify(self, title, message):
        self.tray_icon.showMessage(title, message, BAR_NOTIFICATION_TIME)
