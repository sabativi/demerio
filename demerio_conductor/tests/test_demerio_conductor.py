import unittest
import random
from os.path import join
from watchdog.events import *
from demerio_conductor.demerio_conductor import DemerioConductor
from demerio_split.fec import FileFec
from demerio_split.striping import DemerioSplitError
from demerio_utils.file_utils import *
from demerio_sync.storage_api import StorageAPI
from demerio_sync.storage_manager import StorageManager
from demerio_mapping.mapping_config_parser import MappingConfigParser
from demerio_mapping.mapping import STATE
from mock import MagicMock
from nose.plugins.attrib import attr


def encode_path_raise_exception():
    raise DemerioSplitError()

def mock_decode_path(output_path, chunks):
    create_new_file(output_path)
    for chunk in chunks:
        delete_file(chunk)

def mock_download_file_chunks(chunk_list, output_file_paths):
    for output_file_path in output_file_paths:
        create_new_file(output_file_path)


class TestDemerioHandler(unittest.TestCase):
    """
    This is an integration testCase, we use Mock as storage_manager and
    as split to only test mapping integration
    """

    def _mock_encode_path_in_dir(self, input_path, temp_dir):
        return [generate_random_file_name_in_dir(temp_dir) for i in range(self.m)]

    def _mock_storage_new_file(self, file_parts):
        return [ (generate_random_string(), file_part) for file_part in file_parts ]

    def setUp(self):
        self.m = random.randint(1, 6)
        self.k = self.m - 1
        self.storage_manager = StorageManager()
        self.fec = FileFec(self.k, self.m)
        self.mapping = MappingConfigParser(create_random_dir(), generate_random_file_path())
        self.handler = DemerioConductor(self.mapping, self.fec, self.storage_manager)

    def tearDown(self):
        delete_file(self.mapping.config_file_path)
        delete_dir(self.mapping.base_dir)

    def test_on_created_file_without_error(self):
        # Given
        new_file = generate_random_file_name_in_dir(self.mapping.base_dir)
        created_event = FileCreatedEvent(new_file)
        self.fec.encode_path_in_dir = self._mock_encode_path_in_dir
        self.storage_manager.new_file = self._mock_storage_new_file

        # When
        self.handler.on_created(created_event)

        # Then
        self.assertTrue(self.mapping.has_file(new_file))
        self.assertTrue(self.mapping.get_state(new_file) == STATE.ok)

    def test_on_created_file_with_split_error(self):
        # Given
        new_file = generate_random_file_name_in_dir(self.mapping.base_dir)
        created_event = FileCreatedEvent(new_file)
        self.fec.encode_path_in_dir = MagicMock(side_effect=DemerioSplitError(''))

        # When
        self.handler.on_created(created_event)

        # Then
        self.assertTrue(self.mapping.has_file(new_file))
        self.assertTrue(self.mapping.get_state(new_file) == STATE.detected)

    def test_after_reconstruct_i_have_the_same_number_of_files(self):
        # Given
        number_of_files = random.randint(1, 100)
        for file_number in range(number_of_files):
            file_path = generate_random_file_name_in_dir(self.mapping.base_dir)
            self.mapping.add_file(file_path, self.k, self.m)
            self.mapping.update_to_splitted_state(file_path, [generate_random_string() for i in range(self.m)])
        output_dir = create_random_dir()
        self.addCleanup(lambda: delete_dir(output_dir))
        self.storage_manager.download_file_chunks = mock_download_file_chunks
        self.fec.decode_path = mock_decode_path

        # When
        self.handler.reconstruct_dir(output_dir)

        # Then
        actual_number_of_files = count_files_recursively_in_dir(output_dir)
        self.assertEqual(number_of_files, actual_number_of_files)
