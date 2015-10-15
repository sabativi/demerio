from watchdog.events import LoggingEventHandler
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from demerio_utils.log import *
from demerio_utils.file_utils import *

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

class DemerioConductor(LoggingEventHandler, QObject):
    """
    Handler to operate all operations
    """

    event_started = pyqtSignal()
    event_finished = pyqtSignal()
    conductor_exception = pyqtSignal(Exception)

    def __init__(self, mapping, fec, storage_manager):
        self.mapping = mapping
        self.fec = fec
        self.storage_manager = storage_manager
        LoggingEventHandler.__init__(self)
        QObject.__init__(self)

    @add_signals
    def on_created(self, event):
        super(DemerioConductor, self).on_created(event)
        if not event.is_directory:
            temp_dir = create_random_dir()
            self.mapping.add_file(event.src_path, self.fec.k, self.fec.m)
            try:
                parts = self.fec.encode_path_in_dir(event.src_path, temp_dir)
            except Exception, e:
                print e
                return
            self.mapping.update_to_splitted_state(event.src_path, parts)
            self.mapping.update_to_sync_start_state(event.src_path)
            chunks_list = self.storage_manager.new_file(parts)
            self.mapping.update_to_ok_state(event.src_path, chunks_list)
            delete_dir(temp_dir)

    @add_signals
    def on_deleted(self, event):
        super(DemerioConductor, self).on_deleted(event)
        if event.is_directory:
            files_to_remove = self.mapping.get_files_in_dir(event.src_path)
            chunks_to_remove = [chunk for file_to_remove in files_to_remove for chunk in self.mapping.get_chunks(file_to_remove)]
            self.storage_manager.remove_files(chunks_to_remove)
            self.mapping.remove_dir(event.src_path)
        else:
            self.storage_manager.remove_files(self.mapping.get_chunks(event.src_path))
            self.mapping.remove_file(event.src_path)

    @add_signals
    def on_modified(self, event):
        super(DemerioConductor, self).on_modified(event)
        if not event.is_directory:
            previous_chunks = self.mapping.get_chunks(event.src_path)
            temp_dir = create_random_dir()
            new_parts = self.fec.encode_file(event.src_path, temp_dir)
            self.storage_manager.update_file(previous_chunks, new_parts)
            delete_dir(temp_dir)

    @add_signals
    def on_moved(self, event):
        super(DemerioConductor, self).on_moved(event)
        if event.is_directory:
            self.mapping.rename_dir(event.src_path, event.dest_path)
        else:
            self.mapping.rename_file(event.src_path, event.dest_path)

    def reconstruct_dir(self, output_dir):
        print "reconstruct dir"

