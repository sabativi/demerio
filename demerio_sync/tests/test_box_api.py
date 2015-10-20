import unittest
import os
from nose.plugins.attrib import attr
from demerio_utils.file_utils import create_random_file
from demerio_utils.file_utils import create_random_dir
from demerio_utils.file_utils import delete_file
from demerio_utils.file_utils import delete_dir
from demerio_utils.file_utils import generate_random_file_path
from demerio_utils.file_utils import add_random_content_to_file
from demerio_utils.file_utils import get_size
from demerio_sync.box_api import BoxAPI
from demerio_sync.box_api import BoxAPIException
from selenium import webdriver
from selenium_oauth import authorize_box_user
from selenium_oauth import enter_text_by_id
from selenium_oauth import click_button_by_id
from selenium_oauth import wait_for_code
from selenium_oauth import convert_url_to_query_dict

BOX_EMAIL = "victor.sabatier@gmail.com"
try:
    BOX_PASSWD = os.environ['BOX_PASSWD']
except KeyError:
    exit("box Passwd is not set")


class TestBoxAuth(unittest.TestCase):

    def setUp(self):
        self.tempdir = create_random_dir()
        self.box = BoxAPI(self.tempdir)

    def tearDown(self):
        delete_dir(self.tempdir)

    def test_without_credential_file_i_am_not_connected(self):
        self.assertFalse(self.box.is_connected())

    @attr(slow=True)
    def test_i_can_connect_with_mail_adress_and_password(self):
        # Given
        driver = webdriver.Firefox()
        code = authorize_box_user(driver, self.box.get_auth_url(), BOX_EMAIL, BOX_PASSWD)
        self.box.oauth.authenticate(code)

        # When
        self.box.build()

        # Then
        self.assertTrue(self.box.is_connected())

        # Clean
        driver.quit()

    @attr(slow=True)
    def test_user_cancel_connection(self):
        # Given
        driver = webdriver.Firefox()
        driver.get(self.box.get_auth_url())
        try:
            enter_text_by_id(driver, "login", BOX_EMAIL, False)
            enter_text_by_id(driver, "password", BOX_PASSWD)

        # When
            click_button_by_id(driver, "consent_reject_button")
            wait_for_code(driver, "errorPageContainer")

        except:
            raise Exception("timeout for authorization")

        # Then
        self.assertTrue("error_description" in convert_url_to_query_dict(driver.current_url))
        driver.quit()


class TestBoxApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Firefox()
        cls.tempdir = create_random_dir()
        cls.box = BoxAPI(cls.tempdir)
        code = authorize_box_user(cls.driver, cls.box.get_auth_url(), BOX_EMAIL, BOX_PASSWD)
        access_token, refresh_token = cls.box.oauth.authenticate(code)
        cls.box.write_access_token(access_token, refresh_token)
        cls.box.build()

    @classmethod
    def tearDownClass(cls):
        delete_dir(cls.tempdir)
        cls.driver.quit()

    @attr(slow=True)
    def test_i_do_not_need_to_go_through_oauth_if_file_exists(self):
        # When
        box_new = BoxAPI(self.tempdir)

        # Then
        self.assertTrue(box_new.is_connected())

    @attr(slow=True)
    def test_upload_download_and_delete_new_file(self):
        # Given
        file_path = create_random_file()
        add_random_content_to_file(file_path)
        file_name = "newdatalordstest.dlords"
        out_file = generate_random_file_path()

        # When
        file_id = self.box.upload_new_file(file_path)
        self.box.download_file(file_id, out_file)

        # Then
        self.assertTrue(os.path.exists(out_file))
        self.assertTrue(get_size(out_file) > 0)

        # When
        self.box.delete_file(file_id)

        # Then
        with self.assertRaises(BoxAPIException):
            self.box.client.file(file_id=file_id).get()

        # Clean
        delete_file(file_path)
        delete_file(out_file)
