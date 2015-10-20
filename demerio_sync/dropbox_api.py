from storage_api import StorageAPI
from dropbox import client
import webbrowser
import os
from os.path import join
from oauth2client.tools import ClientRedirectHandler
from oauth2client.tools import ClientRedirectServer
from demerio_utils.file_utils import generate_random_string

CREDENTIAL_FILENAME = 'dropbox.auth'
REDIRECT_URI = "http://localhost:8888/"
ACCESS_TYPE = 'dropbox'
CRSF_TOKEN_KEY = "dropbox-auth-csrf-token"

APP_KEY = 'pnshh3a2cvt3son'
try:
    APP_SECRET = os.environ['DROPBOX_SECRET']
except KeyError:
    exit("App secret env variable for dropbox is not set")

"""
Dropbox api allow us to use file_name instead of file_id
"""


class DropboxAPI(StorageAPI):

    def __init__(self, credential_dir, credential_filename=CREDENTIAL_FILENAME):
        super(DropboxAPI, self).__init__(credential_dir)
        self.auth_file = join(credential_dir, credential_filename)
        self.flow = client.DropboxOAuth2Flow(APP_KEY, APP_SECRET, REDIRECT_URI, {}, "dropbox-auth-csrf-token")
        try:
            access_token = self.get_access_token_from_file()
            self.build(access_token)
        except IOError:
            pass

    def get_auth_url(self):
        return self.flow.start()

    def get_access_token_from_file(self):
        with open(self.auth_file, "r") as f:
            return f.readline().rstrip()

    def authorize(self):
        # TODO : reafactorize with REDIRECT_URI
        if os.path.exists(self.auth_file):
            access_token = self.get_access_token_from_file()
        else:
            httpd = ClientRedirectServer(("localhost", 8888), ClientRedirectHandler)
            webbrowser.open(self.get_auth_url())
            httpd.handle_request()
            access_token, user_id, url_state = self.flow.finish(httpd.query_params)
        self.build(access_token)

    def build(self, access_token):
        with open(self.auth_file, 'w') as file:
            file.write(access_token + "\n")
        self.client = client.DropboxClient(access_token)

    def is_connected(self):
        try:
            self.client.account_info()
        except:
            return False
        return True

    def get_metadata(self, file_name):
        return self.client.metadata(file_name)

    def exists(self, file_name):
        return not self.get_metadata(file_name)["is_deleted"]

    def download_file(self, file_name, path_to_download):
        f = self.client.get_file(file_name)
        with open(path_to_download, 'wb') as out_f:
            out_f.write(f.read())

    def upload_new_file(self, local_file_path):
        file_name = generate_random_string()
        with open(local_file_path, 'rb') as f:
            self.client.put_file(file_name, f, overwrite=False)
        return file_name

    def delete_file(self, file_id):
        self.client.file_delete(file_id)

    def update_file(self, local_file_path, file_id):
        with open(local_file_path, 'rb') as f:
            self.client.put_file(file_id, f, overwrite=True)
