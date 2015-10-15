from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QTimer
import urllib2

class ConnectionHandler(QObject):

    value_changed = pyqtSignal(bool)

    def __init__(self, frequency_check, time_before_time_out, parent=None):
        super(ConnectionHandler, self).__init__(parent)
        self.frequency_check = frequency_check
        self.time_before_time_out = time_before_time_out
        self.internet_ok = None
        self.timer = QTimer(self)

    def start(self):
        self.timer.setInterval(self.frequency_check)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def stop(self):
        self.timer.stop()

    def emit_if_changed(self, new_value):
        if not self.internet_ok is new_value:
            self.internet_ok = new_value
            self.value_changed.emit(new_value)

    def check_internet_call(self):
        urllib2.urlopen('http://www.demerio.com', timeout=self.time_before_time_out)

    @pyqtSlot()
    def update(self):
        try:
            self.check_internet_call()
        except Exception as e:
            self.emit_if_changed(False)
        else:
            self.emit_if_changed(True)
