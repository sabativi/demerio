import unittest
from demerio_utils.file_utils import is_subdirectory
from demerio_utils.file_utils import split_file_with_dir
from demerio_utils.deploy_platform import is_windows


class FileUtilsTest(unittest.TestCase):

    def test_is_subdirectory(self):
        self.assertFalse(is_subdirectory('/var/test2', '/var/test'))
        self.assertFalse(is_subdirectory('/var/test', '/var/test2'))
        self.assertFalse(is_subdirectory('var/test2', 'var/test'))
        self.assertFalse(is_subdirectory('var/test', 'var/test2'))
        self.assertTrue(is_subdirectory('/var/test/sub', '/var/test'))
        self.assertFalse(is_subdirectory('/var/test', '/var/test/sub'))
        self.assertTrue(is_subdirectory('var/test/sub', 'var/test'))
        self.assertTrue(is_subdirectory('var/test', 'var/test'))
        self.assertTrue(is_subdirectory('var/test', 'var/test/fake_sub/..'))
        self.assertTrue(is_subdirectory('var/test/sub/sub2/sub3/../..', 'var/test'))
        self.assertTrue(is_subdirectory('var/test/sub', 'var/test/fake_sub/..'))
        self.assertFalse(is_subdirectory('var/test', 'var/test/sub'))

    def test_split_path_with_dirname(self):
        self.assertEqual(split_file_with_dir('/var/test/sub', '/var/test'), 'sub')
        self.assertEqual(split_file_with_dir('/var/test/sub/titi', '/var/test'), 'sub/titi')
        self.assertEqual(split_file_with_dir('/var/test/sub/fre/frefer', '/var/test'), 'sub/fre/frefer')

    def should_add_test_windows(self):
        if is_windows():
            self.assertFalse(True, "Not implemented on windows")

if __name__ == '__main__':
    unittest.main()
