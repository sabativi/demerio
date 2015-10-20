from storage_api import StorageAPI
import os
from os.path import join
import webbrowser
from boxsdk import OAuth2
from boxsdk import Client
from boxsdk.exception import BoxAPIException
from oauth2client.tools import ClientRedirectHandler
from oauth2client.tools import ClientRedirectServer
from demerio_utils.file_utils import generate_random_string

CREDENTIAL_FILENAME = 'box.auth'
CLIENT_ID = '7kem9tsaa73blf8bt2i7miewqcc8zjb1'
REDIRECT_URI = "http://localhost:8888/"


try:
    CLIENT_SECRET = os.environ['BOX_SECRET']
except KeyError:
    exit("Client secret env variable for box is not set")


class BoxAPI(StorageAPI):

    def __init__(self, credential_dir, credential_filename=CREDENTIAL_FILENAME):
        super(BoxAPI, self).__init__(credential_dir)
        self.auth_file = join(credential_dir, credential_filename)
        self.oauth = OAuth2(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, store_tokens=self.write_access_token)
        try:
            self.get_tokens_from_file()
            self.authorize()
        except IOError:
            pass

    def get_auth_url(self):
        auth_url, csrf_token = self.oauth.get_authorization_url(REDIRECT_URI)
        return auth_url

    def build(self):
        self.client = Client(self.oauth)
        self.create_folder("demerio")

    def create_folder(self, folder_name):
        search_results = self.client.search(folder_name, limit=100, offset=0, ancestor_folders=[self.client.folder(folder_id='0')])
        folder_filter = [result for result in search_results if result._item_type == "folder"]
        if len(folder_filter) == 0:
            demerio_folder = self.client.folder(folder_id='0').create_subfolder('demerio')
        else:
            assert len(folder_filter) == 1
            demerio_folder = folder_filter[0].get(fields=["name"])
        self.root_folder_id = demerio_folder.id

    def get_tokens_from_file(self):
        with open(self.auth_file, "r") as f:
            access_token = f.readline().rstrip()
            refresh_token = f.readline().rstrip()
        return access_token, refresh_token

    def write_access_token(self, access_token, refresh_token):
        with open(self.auth_file, 'w') as f:
            f.write(access_token + "\n")
            f.write(refresh_token + "\n")

    def authorize(self):
        if os.path.exists(self.auth_file):
            access_token, refresh_token = self.get_tokens_from_file()
            self.oauth._access_token = access_token
            self.oauth._refresh_token = refresh_token
        else:
            httpd = ClientRedirectServer(("localhost", 8888), ClientRedirectHandler)
            webbrowser.open(self.get_auth_url())
            httpd.handle_request()
            self.oauth.authenticate(httpd.query_params['code'])
        self.build()

    def is_connected(self):
        ## TODO: There must be a better way to check connection, with self.oauth ??
        try:
            self.client.user(user_id='me').get()
        except:
            return False
        return True

    def download_file(self, file_id, path_to_download):
        with open(path_to_download, "wb") as f:
            f.write(self.client.file(file_id=file_id).content())

    def upload_new_file(self, local_file_path):
        new_file = self.client.folder(folder_id=self.root_folder_id).upload(local_file_path, file_name = generate_random_string())
        return new_file.get()['id']

    def delete_file(self, file_id):
        self.client.file(file_id=file_id).delete()

    def update_file(self, local_file_path, file_id):
        self.client.file(file_id=file_id).update_contents(local_file_path)
