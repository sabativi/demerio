from demerio_conductor import DemerioConductor
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal

def add_signals(func):
    """
    Decorator to send signal before and after event handler so that
    we know where we are processing things
    """
    def wrapper(*args, **kwargs):
        self = args[0]
        self.event_started.emit()
        try:
            func(*args, **kwargs)
        except Exception as e:
            self.conductor_exception.emit(e)
        else:
            self.event_finished.emit()
    return wrapper


class WrapHandler(DemerioConductor, QObject):
    """
    Wrap DemerioConductor so that we can use slot and signals from qt
    TODO: maybe there is a more proper way to do it.
    """

    event_started = pyqtSignal()
    event_finished = pyqtSignal()
    conductor_exception = pyqtSignal(Exception)

    def __init__(self, *args):
        DemerioConductor.__init__(self, *args)
        QObject.__init__(self)

    @add_signals
    def on_modified(self, event):
        DemerioConductor.on_modified(self, event)

    @add_signals
    def on_deleted(self, event):
        DemerioConductor.on_deleted(self, event)

    @add_signals
    def on_moved(self, event):
        DemerioConductor.on_moved(self, event)

    @add_signals
    def on_created(self, event):
        DemerioConductor.on_created(self, event)
