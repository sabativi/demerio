from abc import ABCMeta
from abc import abstractmethod
from os.path import join
from os.path import basename
from os.path import expanduser
from os.path import exists

from demerio_utils.file_utils import create_new_file

DEFAULT_DIR_PATH = join(expanduser("~"), ".datalords")
DEFAULT_CONFIG_FILE_PATH = join(DEFAULT_DIR_PATH, "map")

def Enum(**enums):
    "Tricks to implement enum"
    return type('Enum', (), enums)

OPTION = Enum(needed="k", splitted="m", config="config", base_dir="base_dir", state="state")
STATE = Enum(detected="DETECTED", splitted="SPLITTED", sync_start="SYNC_START", sync_failed="SYNC_FAILED", ok="ok")

class Mapping():

    __metaclass__=ABCMeta

    def __init__(self, base_dir, config_file_path):
        self._base_dir = base_dir
        self._config_file_path = config_file_path
        if not exists(self._config_file_path):
            create_new_file(self._config_file_path)

    @property
    def config_file_path(self):
        return self._config_file_path

    @property
    def base_dir(self):
        return self._base_dir

    @base_dir.setter
    def base_dir(self, new_base_dir):
        self._base_dir = new_base_dir

    @abstractmethod
    def _update(self):
        pass

    @abstractmethod
    def update_to_splitted_state(self, file_path, list_of_parts):
        pass

    @abstractmethod
    def update_to_sync_start_state(self, file_path, list_of_chunks):
        pass

    @abstractmethod
    def update_to_sync_failed_state(self, file_path):
        pass

    @abstractmethod
    def update_to_detected_state(self, file_path):
        pass

    @abstractmethod
    def update_to_ok_state(self, file_path):
        pass

    @abstractmethod
    def add_file(self, file_path, k, m, state):
        pass

    @abstractmethod
    def add_dir(self, dir_path):
        pass

    @abstractmethod
    def remove_file(self):
        pass

    @abstractmethod
    def remove_dir(self, dir_name):
        pass

    @abstractmethod
    def rename_file(self, new_file_name, prev_file_name):
        pass

    @abstractmethod
    def rename_dir(self, prev_dir_name, new_dir_name):
        pass

    @abstractmethod
    def has_file(self, file_path):
        pass





