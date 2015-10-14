from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimer
from params import *
import urllib2


TIME_OUT_CALL_S = 3

class ConnectionHandler(QObject):

    value_changed = pyqtSignal(bool)

    def __init__(self, parent=None):
        super(ConnectionHandler, self).__init__(parent)
        self.internet_ok = None
        self.timer  = QTimer(self)

    def start(self):
        self.timer.setInterval(FREQUENCY_CHECK_MS)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def emit_if_changed(self, new_value):
        if not self.internet_ok is new_value:
            self.internet_ok = new_value
            self.value_changed.emit(new_value)

    def check_internet_call(self):
        urllib2.urlopen('http://www.demerio.com', timeout=TIME_OUT_CALL_S)

    @pyqtSlot()
    def update(self):
        try:
            self.check_internet_call()
        except Exception as e:
            self.emit_if_changed(False)
        else:
            self.emit_if_changed(True)
