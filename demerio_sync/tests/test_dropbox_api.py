import unittest
from nose.plugins.attrib import attr
from demerio_utils.file_utils import add_random_content_to_file
from demerio_utils.file_utils import create_random_dir
from demerio_utils.file_utils import create_random_file
from demerio_utils.file_utils import delete_dir
from demerio_utils.file_utils import generate_random_file_path
from demerio_utils.file_utils import delete_file
from demerio_sync.dropbox_api import DropboxAPI
from selenium import webdriver
from selenium_oauth import enter_text_by_xpath
from selenium_oauth import click_button_by_name
from selenium_oauth import authorize_dropbox_user
from selenium_oauth import wait_for_code
from selenium_oauth import convert_url_to_query_dict
import os

DROPBOX_EMAIL = "victor.sabatier@gmail.com"
try:
    DROPBOX_PASSWD = os.environ['DROPBOX_PASSWD']
except KeyError:
    exit("dropbox Passwd is not set")


class TestDropboxAuth(unittest.TestCase):

    def setUp(self):
        self.tempdir = create_random_dir()
        self.dropbox = DropboxAPI(self.tempdir)

    def tearDown(self):
        delete_dir(self.tempdir)

    def test_without_credential_file_i_am_not_connected(self):
        self.assertFalse(self.dropbox.is_connected())

    @attr(slow=True)
    def test_i_can_connect_with_mail_adress_and_password(self):
        # Given
        driver = webdriver.Firefox()
        params = authorize_dropbox_user(driver, self.dropbox.get_auth_url(), DROPBOX_EMAIL, DROPBOX_PASSWD)
        access_token, user_id, url_state = self.dropbox.flow.finish(params)

        # When
        self.dropbox.build(access_token)

        # Then
        self.assertTrue(self.dropbox.is_connected())

        # Clean
        driver.quit()

    @attr(slow=True)
    def test_user_cancel_connection(self):
        # Given
        driver = webdriver.Firefox()
        driver.get(self.dropbox.get_auth_url())
        try:
            enter_text_by_xpath(driver, "//input[@name='login_email']", DROPBOX_EMAIL, press_return=False)
            enter_text_by_xpath(driver, "//input[@name='login_password']", DROPBOX_PASSWD)

        # When
            click_button_by_name(driver, "deny_access")
            wait_for_code(driver, "errorPageContainer")

        except:
            raise Exception("timeout for authorization")

        # Then
        self.assertTrue("error_description" in convert_url_to_query_dict(driver.current_url))
        driver.quit()


class TestDropboxApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox()
        cls.tempdir = create_random_dir()
        cls.dropbox = DropboxAPI(cls.tempdir)
        params = authorize_dropbox_user(cls.driver, cls.dropbox.get_auth_url(), DROPBOX_EMAIL, DROPBOX_PASSWD)
        access_token, user_id, url_state = cls.dropbox.flow.finish(params)
        cls.dropbox.build(access_token)

    @classmethod
    def tearDownClass(cls):
        delete_dir(cls.tempdir)
        cls.driver.quit()

    @attr(slow=True)
    def test_i_do_not_need_to_go_through_oauth_if_file_exists(self):
        # When
        dropbox_new = DropboxAPI(self.tempdir)

        # Then
        self.assertTrue(dropbox_new.is_connected())

    @attr(slow=True)
    def test_download_file(self):
        # Given
        out_file = generate_random_file_path()

        # When
        self.dropbox.download_file("datalords-test.txt", out_file)

        # Then
        self.assertTrue(os.path.exists(out_file))

        # Clean
        delete_file(out_file)

    @attr(slow=True)
    def test_upload_and_delete_new_file(self):
        # Given
        file_path = create_random_file()
        add_random_content_to_file(file_path)
        file_name = "newdatalordstest"

        # When
        file_name = self.dropbox.upload_new_file(file_path)

        # Then
        metadata = self.dropbox.get_metadata(file_name)
        self.assertEqual(metadata['path'], '/' + file_name)

        # When
        self.dropbox.delete_file(file_name)

        # Then
        self.assertFalse(self.dropbox.exists(file_name))

        # Clean
        delete_file(file_path)
