from abc import ABCMeta
from abc import abstractmethod
from demerio_utils.file_utils import create_new_dir
from os.path import exists
from os.path import expanduser
from os.path import join

CREDENTIAL_DIR = join(expanduser("~"), ".demerio")


class TooManyFilesFoundError(Exception):
    pass


class NoFilesFoundError(Exception):
    pass


class StorageAPI():

    __metaclass__=ABCMeta

    def __init__(self, credential_dir=CREDENTIAL_DIR):
        self.credential_dir = credential_dir
        if not exists(credential_dir):
            create_new_dir(credential_dir)

    @abstractmethod
    def authorize(self):
        """
        Should handle authentification, oauth2 for most cases
        """
        pass

    @abstractmethod
    def is_connected(self):
        """
        return True is service is connected
        """
        pass

    @abstractmethod
    def download_file(self, file_id, path_to_download):
        """
        Download file_id to path_to_download location
        """
        pass

    @abstractmethod
    def upload_new_file(self, local_file_path):
        """
        Upload new file, must return the new file id created
        """
        pass

    @abstractmethod
    def delete_file(self, file_id):
        """
        Delete file by id
        """
        pass

    @abstractmethod
    def update_file(self, local_file_path, file_id):
        """
        Update file_id with content form local_file_path
        """
        pass
