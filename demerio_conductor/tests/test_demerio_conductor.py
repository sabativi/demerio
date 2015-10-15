import unittest
import random
from os.path import join
from watchdog.events import *
from demerio_conductor.demerio_conductor import DemerioConductor
from demerio_split.striping import Striping
from demerio_split.striping import DemerioSplitError
from demerio_utils.file_utils import *
from demerio_sync.storage_api import StorageAPI
from demerio_sync.storage_manager import StorageManager
from demerio_mapping.mapping_config_parser import MappingConfigParser
from demerio_mapping.mapping import STATE
from mock import MagicMock


def encode_path_raise_exception():
    raise DemerioSplitError()

class MockFec(Striping):
    """Spliting that do nothing"""
    def __init__(self, k, m):
        super(MockFec, self).__init__(k, m)

    def encode_path_in_dir(self, input_path, temp_dir):
        return [input_path]

    def decode_path(self, output_path, chunks):
        pass

class MockStorage(StorageAPI):
    def __init__(self, credential_dir):
        pass

    def authorize(self):
        pass

    def is_connected(self):
        pass

    def download_file(self, file_id, path_to_download):
        pass

    def upload_new_file(self, local_file_path):
        return generate_random_string()

    def delete_file(self, file_id):
        pass

    def update_file(self, local_file_path, file_id):
        pass


class TestDemerioHandler(unittest.TestCase):
    """
    This is an integration testCase, we use Mock as storage_manager and
    as split to only test mapping integration
    """

    def setUp(self):
        m = random.randint(1, 6)
        self.storage_manager = StorageManager()
        for i in range(m):
            self.storage_manager.add_storage("disk" + str(i), MockStorage(""))
        self.fec = MockFec(m-1, m)
        self.listen_dir = create_random_dir()
        self.mapping = MappingConfigParser(self.listen_dir)
        self.handler = DemerioConductor(self.mapping, self.fec, self.storage_manager)

    def tearDown(self):
        pass

    def test_on_created_file_without_error(self):
        # Given
        new_file = generate_random_file_name_in_dir(self.listen_dir)
        created_event = FileCreatedEvent(new_file)

        # When
        self.handler.on_created(created_event)

        # Then
        self.assertTrue(self.mapping.has_file(new_file))
        self.assertTrue(self.mapping.get_state(new_file) == STATE.ok)

    def test_on_created_file_with_split_error(self):
        # Given
        new_file = generate_random_file_name_in_dir(self.listen_dir)
        created_event = FileCreatedEvent(new_file)
        self.fec.encode_path_in_dir = MagicMock(side_effect=DemerioSplitError(''))

        # When
        self.handler.on_created(created_event)

        # Then
        self.assertTrue(self.mapping.has_file(new_file))
        self.assertTrue(self.mapping.get_state(new_file) == STATE.detected)

