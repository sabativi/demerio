from ConfigParser import SafeConfigParser
from os.path import dirname
from os.path import join
from os.path import basename
from demerio_utils.file_utils import create_new_file
from demerio_utils.file_utils import is_subdirectory
from demerio_utils.file_utils import split_file_with_dir
from demerio_utils.file_utils import is_file_path
from mapping import Mapping
from mapping import OPTION
from mapping import STATE
from mapping import DEFAULT_CONFIG_FILE_PATH


def modTupByIndex(tup, index, ins):
    lst = list(tup)
    lst[index] = ins
    return tuple(lst)


class NotInBaseDirException(Exception):
    pass


def check_in_base_dir(func):
    """
    Decorator to check that the file_path received is in
    the base_dir of the Mapping
    """
    def decorated(*args, **kwargs):
        base_dir = args[0].base_dir
        file_path = args[1]
        if not is_subdirectory(dirname(file_path), base_dir):
            raise NotInBaseDirException
        return func(*args, **kwargs)
    return decorated


def convert_to_filename(func):
    """
    Decorator to convert file_path with file_name in
    base_dir
    """
    def decorated(*args, **kwargs):
        if is_file_path(args[1]):
            args = modTupByIndex(args, 1, split_file_with_dir(args[1], args[0].base_dir))
        return func(*args, **kwargs)
    return decorated


class MappingConfigParser(Mapping):
    """
    base_dir : main directory where all the files are
    config_file_path : where the file is saved
    """

    def __init__(self, base_dir, config_file_path=DEFAULT_CONFIG_FILE_PATH):
        super(MappingConfigParser, self).__init__(base_dir, config_file_path)
        self.parser = SafeConfigParser()
        self.parser.read(self._config_file_path)
        self._create_config_section()

    def _create_config_section(self):
        if not self.parser.has_section(OPTION.config):
            self.parser.add_section(OPTION.config)
            self.parser.set(OPTION.config, OPTION.base_dir, self._base_dir)

    @property
    def config_file_path(self):
        return self._config_file_path

    @property
    def base_dir(self):
        return self._base_dir

    @base_dir.setter
    def base_dir(self, new_base_dir):
        self._base_dir = new_base_dir

    def _update(self):
        """
        Write the new config to the file
        """
        with open(self._config_file_path, 'w') as f:
            self.parser.write(f)

    @check_in_base_dir
    @convert_to_filename
    def add_file(self, file_path, k, m, state=STATE.detected):
        self._add_file(file_path, k, m, state)

    def add_dir(self, dir_path):
        pass

    def _add_file(self, file_name, k, m, state):
        self.parser.add_section(file_name)
        self.parser.set(file_name, OPTION.needed, str(k))
        self.parser.set(file_name, OPTION.splitted, str(m))
        self.parser.set(file_name, OPTION.state, state)
        self._update()

    @convert_to_filename
    def update_to_splitted_state(self, file_path, list_of_parts):
        for number, part in enumerate(list_of_parts):
            self.parser.set(file_path, str(number), part)
        self._update_state(file_path, STATE.splitted)

    @convert_to_filename
    def update_to_sync_start_state(self, file_path):
        self._update_state(file_path, STATE.sync_start)

    @convert_to_filename
    def update_to_sync_failed_state(self, file_path):
        self._update_state(file_path, STATE.sync_failed)

    @convert_to_filename
    def update_to_detected_state(self, file_path):
        self._update_state(file_path, STATE.detected)

    @convert_to_filename
    def update_to_ok_state(self, file_path, list_of_chunks):
        self.update_chunks_for_file(file_path, list_of_chunks)
        self._update_state(file_path, STATE.ok)

    def _update_state(self, file_path, state):
        self.parser.remove_option(file_path, OPTION.state)
        self.parser.set(file_path, OPTION.state, state)
        self._update()

    @convert_to_filename
    def remove_file(self, file_path):
        self._remove_file(file_path)

    def _remove_file(self, file_name):
        self.parser.remove_section(file_name)
        self._update()

    @convert_to_filename
    def update_parts_numbers(self, file_path, k, m):
        self.parser.remove_option(file_path, OPTION.needed)
        self.parser.set(file_path, OPTION.needed, str(k))
        self.parser.remove_option(file_path, OPTION.splitted)
        self.parser.set(file_path, OPTION.splitted, str(m))

    @convert_to_filename
    def update_chunks_for_file(self, file_path, new_chunks):
        for chunk in self._get_chunks(file_path):
            self.parser.remove_option(file_path, chunk[0])
        for chunk in new_chunks:
            self.parser.set(file_path, chunk[0], chunk[1])

    def remove_dir(self, dir_name):
        for file_name in self.parser.sections():
            if is_subdirectory(dirname(join(self._base_dir, file_name)), dir_name):
                self._remove_file(file_name)

    def rename_dir(self, prev_dir_name, new_dir_name):
        for file_name in self.parser.sections():
            if is_subdirectory(dirname(join(self._base_dir, file_name)), prev_dir_name):
                k, m = self._get_split_info(file_name)
                chunks = self._get_chunks(file_name)
                state = self._get_state(file_name)
                new_file_path = join(new_dir_name, basename(file_name))
                self.add_file(new_file_path, k, m, state)
                self.update_chunks_for_file(new_file_path, chunks)
                self._remove_file(file_name)

    @check_in_base_dir
    def rename_file(self, new_file_name, prev_file_name):
        k, m = self.get_split_info(prev_file_name)
        chunks = self.get_chunks(prev_file_name)
        state = self.get_state(prev_file_name)
        self.remove_file(prev_file_name)
        self.add_file(new_file_name, k, m, state=state)
        self.update_chunks_for_file(new_file_name, chunks)

    def _get_split_info(self, file_name):
        return self.parser.getint(file_name, OPTION.needed), self.parser.getint(file_name, OPTION.splitted)

    @convert_to_filename
    def get_split_info(self, file_path):
        return self._get_split_info(file_path)

    def _get_state(self, file_name):
        return self.parser.get(file_name, OPTION.state)

    @convert_to_filename
    def get_state(self, file_path):
        return self._get_state(file_path)

    def get_number_of_files(self):
        """-1 is because of the config section"""
        return len(self.get_all_relatives_file_name())

    def get_files_in_dir(self, dir_name):
        return [file_path for file_path in self.parser.sections() if is_subdirectory(dirname(join(self._base_dir, file_path)), dir_name)]

    @convert_to_filename
    def has_file(self, file_path):
        return self.parser.has_section(file_path)

    @convert_to_filename
    def get_chunks(self, file_path):
        return self._get_chunks(file_path)

    def _get_chunks(self, file_name):
        res = [item for item in self.parser.items(file_name) if not item[0] in (OPTION.needed, OPTION.splitted, OPTION.state)]
        return res

    def get_all_relatives_file_name(self):
        all_sections = self.parser.sections()
        all_sections.remove(OPTION.config)
        return all_sections
