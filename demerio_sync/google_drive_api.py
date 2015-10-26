import os
from os.path import join
from pydrive.auth import GoogleAuth
from pydrive.auth import AuthenticationRejected
from pydrive.auth import AuthenticationError
from pydrive.drive import GoogleDrive
from storage_api import StorageAPI
from storage_api import NoFilesFoundError
from storage_api import TooManyFilesFoundError
from demerio_utils.file_utils import generate_random_string
import yaml
from demerio_utils.log import logger

CREDENTIAL_FILENAME = 'google_drive.auth'
CONFIG_FILENAME = 'config.yaml'
CLIENT_ID = '91269595727-098e53udeic4d3u3t1nqinogq69pg1e2.apps.googleusercontent.com'

try:
    CLIENT_SECRET = os.environ['GOOGLE_DRIVE_SECRET']
except KeyError:
    exit("Client secret env variable for google drive is not set")

YAML_CONFIG = """
client_config_backend: settings
client_config:
    client_id: %s
    client_secret: %s
save_credentials: True
save_credentials_backend: file
save_credentials_file: %s
get_refresh_token: True
"""


class GoogleDriveAPI(StorageAPI):

    def __init__(self, credential_dir, credential_filename=CREDENTIAL_FILENAME, config_filename=CONFIG_FILENAME):
        super(GoogleDriveAPI, self).__init__(credential_dir)
        self._writeYamlConfigFile(credential_dir, credential_filename, config_filename)
        self.gauth = GoogleAuth(self.yaml_config_file)
        self.gauth.LoadCredentialsFile(self.credential_path)
        try:
            self.gauth.Authorize()
            self.build()
        except Exception, e:
            pass


    def is_connected(self):
        return not self.gauth.access_token_expired

    def authorize(self):
        try:
            self.gauth.LocalWebserverAuth()
        except (AuthenticationRejected, AuthenticationError):
            logger.debug("Error durring Authentification")
        self.gauth.Authorize()
        self.build()

    def authorize_with_code(self, code):
        self.gauth.Auth(code)

    def build(self):
        self.drive = GoogleDrive(self.gauth)
        self.gauth.SaveCredentialsFile(self.credential_path)
        self.create_demerio_folder()

    def create_demerio_folder(self):
        ## a bit messy here because we use both pydrive and google drive module
        ## which have different level of abstraction
        param = { "q" : "mimeType = 'application/vnd.google-apps.folder' and title = 'demerio'" }
        results = self.gauth.service.files().list(**param).execute()['items']
        if len(results) == 1:
            self.root_folder_id = results[0]['id']
        else:
            demerio_folder = self.drive.CreateFile({'title': "demerio",
                                                      "mimeType": "application/vnd.google-apps.folder"})
            demerio_folder.Upload()
            self.root_folder_id = demerio_folder.metadata.get("id")

    def get_auth_url(self):
        return self.gauth.GetAuthUrl()

    def _writeYamlConfigFile(self, credential_dir, credential_filename, config_filename):
        self.credential_path = join(credential_dir, credential_filename)
        self.yaml_config_file = join(credential_dir, config_filename)
        with open(self.yaml_config_file, 'w') as yaml_file:
            yaml.dump(yaml.load(YAML_CONFIG % (CLIENT_ID, CLIENT_SECRET, self.credential_path)), yaml_file)

    def download_file(self, file_id, path_to_download):
        drive_file = self.drive.CreateFile({'id': file_id})
        drive_file.GetContentFile(path_to_download)

    def upload_new_file(self, local_file_path):
        drive_file = self.drive.CreateFile({'title': generate_random_string(), 'parents': [{'id': self.root_folder_id}]})
        drive_file.SetContentFile(local_file_path)
        drive_file.Upload()
        return drive_file.metadata.get('id')

    def delete_file(self, file_id):
        self._delete_object(file_id)

    def delete_demerio_folder(self):
        self._delete_object(self.root_folder_id)

    def _delete_object(self, object_id):
        param = {'fileId': object_id}
        self.gauth.service.files().delete(**param).execute()

    def update_file(self, local_file_path, file_id):
        drive_file = self.drive.CreateFile({'id': file_id})
        drive_file.SetContentFile(local_file_path)
        drive_file.Upload()
