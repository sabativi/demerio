from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import urlparse
from demerio_utils.log import *
from selenium.webdriver.remote.remote_connection import LOGGER
LOGGER.setLevel(logging.WARNING)

TIME_TO_WAIT = 10


def convert_url_to_query_dict(url):
    return dict(urlparse.parse_qsl(urlparse.urlsplit(url).query))


def enter_text_by_id(driver, id, content, press_return=True):
    wait = WebDriverWait(driver, TIME_TO_WAIT)
    element = wait.until(EC.element_to_be_clickable((By.ID, id)))
    element.send_keys(content)
    if press_return:
        element.send_keys(Keys.RETURN)


def click_button_by_id(driver, id):
    wait = WebDriverWait(driver, TIME_TO_WAIT)
    btn = wait.until(EC.element_to_be_clickable((By.ID, id)))
    btn.click()


def enter_text_by_xpath(driver, xpath, content, press_return=True):
    wait = WebDriverWait(driver, TIME_TO_WAIT)
    element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    element.send_keys(content)
    if press_return:
        element.send_keys(Keys.RETURN)


def click_button_by_name(driver, name):
    wait = WebDriverWait(driver, TIME_TO_WAIT)
    btn = wait.until(EC.element_to_be_clickable((By.NAME, name)))
    btn.click()


def get_code_in_title(driver, code_id):
    wait = WebDriverWait(driver, TIME_TO_WAIT)
    wait.until(EC.title_contains(code_id))
    return driver.title.split("=")[1]


def wait_for_code(driver, id):
    wait = WebDriverWait(driver, TIME_TO_WAIT)
    wait.until(EC.presence_of_element_located((By.ID, id)))


def authorize_drive_user(driver, url, email, passwd):
    driver.get(url)
    try:
        enter_text_by_id(driver, "Email", email)
        enter_text_by_id(driver, "Passwd", passwd)
        click_button_by_id(driver, "submit_approve_access")
        code = get_code_in_title(driver, "Success code")
    except:
        raise Exception("timeout for authorization")
    return code


def authorize_dropbox_user(driver, url, email, passwd):
    driver.get(url)
    try:
        enter_text_by_xpath(driver, "//input[@name='login_email']", email, press_return=False)
        enter_text_by_xpath(driver, "//input[@name='login_password']", passwd)
        click_button_by_name(driver, "allow_access")
        wait_for_code(driver, "errorPageContainer")
    except:
        raise Exception("timeout for authorization")
    return convert_url_to_query_dict(driver.current_url)


def authorize_box_user(driver, url, email, passwd):
    driver.get(url)
    try:
        enter_text_by_id(driver, "login", email, False)
        enter_text_by_id(driver, "password", passwd)
        click_button_by_id(driver, "consent_accept_button")
        wait_for_code(driver, "errorPageContainer")
    except:
        raise Exception("timeout for authorization")
    return convert_url_to_query_dict(driver.current_url)['code']
