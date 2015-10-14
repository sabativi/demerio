import unittest
from nose.plugins.attrib import attr
from demerio_utils.file_utils import create_random_dir
from demerio_utils.file_utils import create_random_file
from demerio_utils.file_utils import delete_file
from demerio_utils.file_utils import delete_dir
from demerio_utils.file_utils import generate_random_file_path
from demerio_utils.file_utils import add_random_content_to_file
from demerio_utils.file_utils import generate_random_string
from demerio_utils.file_utils import get_size
from demerio_sync.google_drive_api import GoogleDriveAPI
from demerio_sync.google_drive_api import NoFilesFoundError
from selenium import webdriver
from selenium_oauth import authorize_drive_user
from selenium_oauth import enter_text_by_id
from selenium_oauth import click_button_by_id
from selenium_oauth import wait_for_code
import os

DRIVE_EMAIL = "victor.sabatier"
try:
    DRIVE_PASSWD = os.environ['DRIVE_PASSWD']
except KeyError:
    exit("drive Passwd is not set")


class TestGoogleDriveAuth(unittest.TestCase):

    def setUp(self):
        self.tempdir = create_random_dir()
        self.google_drive = GoogleDriveAPI(self.tempdir)

    def tearDown(self):
        delete_dir(self.tempdir)

    def test_without_credential_file_i_am_not_connected(self):
        self.assertFalse(self.google_drive.is_connected())

    @attr(slow=True)
    def test_i_can_connect_with_mail_adress_and_password(self):
        # Given
        driver = webdriver.Firefox()
        code = authorize_drive_user(driver, self.google_drive.get_auth_url(), DRIVE_EMAIL, DRIVE_PASSWD)

        # When
        self.google_drive.authorize_with_code(code)

        # Then
        self.assertTrue(self.google_drive.is_connected())
        driver.quit()

    @attr(slow=True)
    def test_user_cancel_connection(self):
        # Given
        driver = webdriver.Firefox()
        driver.get(self.google_drive.get_auth_url())
        try:
            enter_text_by_id(driver, "Email", DRIVE_EMAIL)
            enter_text_by_id(driver, "Passwd", DRIVE_PASSWD)

        # When
            click_button_by_id(driver, "submit_deny_access")
            wait_for_code(driver, 'access_denied')
        except:
            raise Exception("timeout for authorization")

        # Then
        driver.quit()


class TestGoogleDriveApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox()
        cls.tempdir = create_random_dir()
        cls.google_drive = GoogleDriveAPI(cls.tempdir)
        code = authorize_drive_user(cls.driver, cls.google_drive.get_auth_url(), DRIVE_EMAIL, DRIVE_PASSWD)
        cls.google_drive.authorize_with_code(code)
        cls.google_drive.build()

    @classmethod
    def tearDownClass(cls):
        delete_dir(cls.tempdir)
        cls.driver.quit()

    @attr(slow=True)
    def test_demerio_folder_id_is_not_none(self):
        self.assertIsNotNone(self.google_drive.root_folder_id)

    @attr(slow=True)
    def test_i_do_not_need_to_go_through_oauth_if_file_exists(self):
        # Given
        google_drive_new = GoogleDriveAPI(self.tempdir)

        # Then
        self.assertTrue(google_drive_new.is_connected())

    @attr(slow=True)
    def test_upload_download_update_and_delete_new_file(self):
        # Given
        file_path = create_random_file()
        add_random_content_to_file(file_path)
        previous_size = get_size(file_path)
        file_name = "newdatalordstest"
        out_file = generate_random_file_path()

        # When
        file_id = self.google_drive.upload_new_file(file_path)
        add_random_content_to_file(file_path)
        self.google_drive.update_file(file_path, file_id)
        self.google_drive.download_file(file_id, out_file)

        # Then
        self.assertTrue(os.path.exists(out_file))
        self.assertTrue(get_size(out_file) > previous_size)

        # When
        self.google_drive.delete_file(file_id)

        # Then
        # with self.assertRaises():
        self.google_drive.drive.CreateFile({'id' : file_id})

        # Clean
        delete_file(file_path)
