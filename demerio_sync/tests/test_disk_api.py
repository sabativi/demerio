import unittest
from demerio_sync.disk_api import DiskAPI
from demerio_utils.file_utils import create_random_dir
from demerio_utils.file_utils import delete_dir
from demerio_utils.file_utils import generate_random_string
from demerio_utils.file_utils import get_number_of_files_in_dir
from demerio_utils.file_utils import delete_file
from demerio_utils.file_utils import create_random_file
from demerio_utils.file_utils import create_new_file
from os.path import join


class TestDiskApi(unittest.TestCase):

    def setUp(self):
        self.tempdir = create_random_dir()
        self.disk = DiskAPI(self.tempdir)

    def tearDown(self):
        delete_dir(self.tempdir)

    def test_upload_new_file(self):
        # Given
        tempfile = create_random_file()

        # When
        self.disk.upload_new_file(tempfile)

        # Then
        self.assertEqual(get_number_of_files_in_dir(self.tempdir), 1)

        # Clean
        delete_file(tempfile)

    def test_download_file(self):
        # Given
        new_file_name = generate_random_string()
        create_new_file(join(self.tempdir, new_file_name))
        download_dir = create_random_dir()

        # When
        self.disk.download_file(new_file_name, download_dir)

        # Then
        self.assertEqual(get_number_of_files_in_dir(download_dir), 1)

        # Clean
        delete_dir(download_dir)

    def test_delete_file(self):
        new_file_name = generate_random_string()
        create_new_file(join(self.tempdir, new_file_name))

        # When
        self.disk.delete_file(new_file_name)

        # Then
        self.assertEqual(get_number_of_files_in_dir(self.tempdir), 0)
