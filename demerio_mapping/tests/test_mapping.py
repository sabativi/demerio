import unittest
import uuid
import random
from os.path import join
from ConfigParser import NoSectionError
from nose.plugins.attrib import attr
from demerio_mapping.mapping_config_parser import MappingConfigParser as Mapping
from demerio_mapping.mapping_config_parser import NotInBaseDirException
from demerio_mapping.mapping import STATE
from demerio_utils.file_utils import *

MIN_NUM_PARTS = 2
MAX_NUM_PARTS = 8


def generate_file_split_numbers():
    number_of_splitted_parts = random.randint(MIN_NUM_PARTS, MAX_NUM_PARTS)
    number_of_necessitary_parts = random.randint(1, number_of_splitted_parts - 1)
    return number_of_necessitary_parts, number_of_splitted_parts


def generate_random_chunks():
    return [(str(uuid.uuid4()), str(uuid.uuid4())) for i in range(random.randint(MIN_NUM_PARTS, MAX_NUM_PARTS))]


def generate_random_parts():
    return [str(uuid.uuid4()) for i in range(random.randint(MIN_NUM_PARTS, MAX_NUM_PARTS))]

class MappingTest(unittest.TestCase):

    def setUp(self):
        base_dir = create_random_dir()
        config_file_path = create_random_file()
        self.mapping = Mapping(base_dir, config_file_path)

    def tearDown(self):
        delete_file(self.mapping.config_file_path)
        delete_dir(self.mapping.base_dir)

    def _add_file_path_with_random_number(self, file_path):
        self._add_file_path_to_map(file_path, *generate_file_split_numbers())

    def _add_file_path_to_map(self, file_path, k, m):
        self.mapping.add_file(file_path, k, m)

    def _add_random_file_to_map(self, k, m):
        file_path = generate_random_file_name_in_dir(self.mapping.base_dir)
        self._add_file_path_to_map(file_path, k, m)
        return file_path

    def _add_random_file_with_random_numbers_to_map(self):
        return self._add_random_file_to_map(*generate_file_split_numbers())

    def test_add_file(self):
        # Given
        file_path = generate_random_file_name_in_dir(self.mapping.base_dir)
        k, m = generate_file_split_numbers()

        # When
        self.mapping.add_file(file_path, k, m)

        # Then
        self.assertTrue(self.mapping.has_file(file_path))
        self.assertEqual(self.mapping.get_split_info(file_path), (k, m))

    def test_remove_file(self):
        # Given
        file_path = self._add_random_file_with_random_numbers_to_map()

        # When
        self.mapping.remove_file(file_path)

        # Then
        self.assertFalse(self.mapping.has_file(file_path))

    def test_add_multiple_files(self):
        # Given
        expected_number_of_files = random.randint(2, 99)
        [self._add_random_file_with_random_numbers_to_map() for i in range(expected_number_of_files)]

        # When
        actual_number_of_files = self.mapping.get_number_of_files()

        # Then
        self.assertEqual(expected_number_of_files, actual_number_of_files)

    def test_update_to_splitted_state(self):
        # Given
        file_path = self._add_random_file_with_random_numbers_to_map()
        file_parts = generate_random_parts()

        # When
        self.mapping.update_to_splitted_state(file_path, file_parts)

        # Then
        self.assertEqual(len(self.mapping.get_chunks(file_path)), len(file_parts))

    def test_update_to_ok_state(self):
        # Given
        file_path = self._add_random_file_with_random_numbers_to_map()
        parts = generate_random_parts()
        self.mapping.update_to_splitted_state(file_path, parts)
        chunks = [(generate_random_string(), part) for part in parts]

        # When
        self.mapping.update_to_ok_state(file_path, chunks)

        # Then
        self.assertEqual(len(self.mapping.get_chunks(file_path)), len(parts))

    def test_changed_parts_file_numbers(self):
        # Given
        file_path = self._add_random_file_with_random_numbers_to_map()
        new_file_split_numbers = generate_file_split_numbers()

        # When
        self.mapping.update_parts_numbers(file_path, *new_file_split_numbers)

        # Then
        actual_parts = self.mapping.get_split_info(file_path)

        self.assertEqual(actual_parts[0], new_file_split_numbers[0])
        self.assertEqual(actual_parts[1], new_file_split_numbers[1])

    def test_delete_dir(self):
        # Given
        dirname = create_random_dir(dirname=self.mapping.base_dir)
        self._add_file_path_with_random_number(generate_random_file_name_in_dir(dirname))
        self._add_file_path_with_random_number(generate_random_file_name_in_dir(dirname))
        self._add_random_file_with_random_numbers_to_map()

        # When
        self.mapping.remove_dir(dirname)

        # Then
        expected_number_of_files = 1
        actual_number_of_files = self.mapping.get_number_of_files()
        self.assertEqual(actual_number_of_files, expected_number_of_files)

        # Clean
        delete_dir(dirname)

    def test_get_file_in_dir(self):
        # Given
        dirname = create_random_dir(dirname=self.mapping.base_dir)
        expected_number_of_files = random.randint(2, 99)
        for i in range(expected_number_of_files):
            self._add_file_path_with_random_number(generate_random_file_name_in_dir(dirname))

        # When
        actual_number_of_files = len(self.mapping.get_files_in_dir(dirname))

        # Then
        self.assertEqual(actual_number_of_files, expected_number_of_files)

        # Clean
        delete_dir(dirname)

    def test_move_dir(self):
        # Given
        prev_dirname = create_random_dir(dirname=self.mapping.base_dir)
        self._add_file_path_with_random_number(generate_random_file_name_in_dir(prev_dirname))
        self._add_file_path_with_random_number(generate_random_file_name_in_dir(prev_dirname))
        self._add_random_file_with_random_numbers_to_map()
        new_dirname = create_random_dir(dirname=self.mapping.base_dir)

        # When
        self.mapping.rename_dir(prev_dirname, new_dirname)

        # Then
        actual_number_of_files_in_previous_dir = len(self.mapping.get_files_in_dir(prev_dirname))
        self.assertEqual(actual_number_of_files_in_previous_dir, 0)

        actual_number_of_files_in_new_dir = len(self.mapping.get_files_in_dir(new_dirname))
        self.assertEqual(actual_number_of_files_in_new_dir, 2)

        actual_number_of_files = self.mapping.get_number_of_files()
        self.assertEqual(actual_number_of_files, 3)

        # Clean
        delete_dir(prev_dirname)

    def test_rename_file(self):
        # Given
        prev_file_path = self._add_random_file_with_random_numbers_to_map()
        self.mapping.update_to_splitted_state(prev_file_path, generate_random_parts())
        new_file_path = generate_random_file_name_in_dir(dirname=self.mapping.base_dir)
        expected_number_of_chunks = len(self.mapping.get_chunks(prev_file_path))

        # When
        self.mapping.rename_file(new_file_path, prev_file_path)

        # Then
        with self.assertRaises(NoSectionError):
            self.mapping.get_chunks(prev_file_path)
        self.assertEqual(len(self.mapping.get_chunks(new_file_path)), expected_number_of_chunks)

    def test_change_base_dir(self):
        # Given
        file_path = self._add_random_file_with_random_numbers_to_map()
        relative_file_name = split_file_with_dir(file_path, self.mapping.base_dir)
        new_base_dir = create_random_dir()
        new_file_path = join(new_base_dir, relative_file_name)

        # When
        self.mapping.base_dir = new_base_dir

        # Then
        self.assertTrue(self.mapping.has_file(new_file_path))

    def test_add_file_name_not_in_base_dir_raise_exception(self):
        with self.assertRaises(NotInBaseDirException):
            self.mapping.add_file(generate_random_file_path())

    def test_i_can_retrieve_current_state(self):
        # Given
        file_path = self._add_random_file_with_random_numbers_to_map()

        # When
        self.mapping.update_to_detected_state(file_path)

        # Then
        self.assertEqual(self.mapping.get_state(file_path), STATE.detected)

    def test_i_can_get_all_files(self):
        # Given
        number_of_files = random.randint(1, 100)
        list_of_files = [self._add_random_file_with_random_numbers_to_map() for i in range(number_of_files)]

        # When
        actual_files = self.mapping.get_all_relatives_file_name()
        actual_number_of_files = len(actual_files)
        print actual_files

        # Then
        self.assertEqual(actual_number_of_files, number_of_files)
        self.assertTrue(set(actual_files), list_of_files)

