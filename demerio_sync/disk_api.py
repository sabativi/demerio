from storage_api import StorageAPI
from demerio_utils.file_utils import copy_file
from demerio_utils.file_utils import delete_file
from demerio_utils.file_utils import create_new_dir
from os.path import exists
from os.path import join
from os.path import basename


class DiskAPI(StorageAPI):
    """
    We simulate a cloud as a directory in our filesystem.
    Every file uploaded end there.
    We reference the file_id as the relative path of the file from the upload_dir directory
    """

    def __init__(self, upload_dir):
        self._upload_dir = upload_dir
        if not exists(self._upload_dir):
            create_new_dir(self._upload_dir)

    @property
    def upload_dir(self):
        return self._upload_dir

    def authorize(self):
        pass

    def is_connected(self):
        return True

    def download_file(self, file_id, path_to_download):
        copy_file(join(self.upload_dir, file_id), path_to_download)

    def upload_new_file(self, local_file_path):
        file_name = basename(local_file_path)
        copy_file(local_file_path, join(self.upload_dir, file_name))
        return file_name

    def delete_file(self, file_id):
        delete_file(join(self.upload_dir, file_id))

    def update_file(self, local_file_path, file_id):
        self.upload_new_file(local_file_path, file_name)
