from os.path import basename


class StorageManager(object):

    def __init__(self):
        self.map_of_storage = {}

    def add_storage(self, storage_name, storage_api):
        self.map_of_storage[storage_name] = storage_api

    def remove_storage(self, storage_name):
        del self.map_of_storage[storage_name]

    def get_number_of_storages(self):
        return len(self.map_of_storage.keys())

    def new_file(self, list_of_parts):
        ## TODO: ugly change this
        chunks = zip(self.map_of_storage.keys(), list_of_parts)
        res = []
        for storage_name, part in chunks:
            cloud_file_id = self.map_of_storage[storage_name].upload_new_file(part)
            res.append((storage_name, cloud_file_id))
        return res

    def update_file(self, previous_chunk, new_list_of_parts):
        for ((storage_name, cloud_file_name), part) in zip(previous_chunk, new_list_of_parts):
            self.map_of_storage[storage_name].update_file(part, cloud_file_name)

    def remove_file_chunks(self, chunk_list):
        for (storage_name, cloud_file_name) in chunk_list:
            self.map_of_storage[storage_name].delete_file(cloud_file_name)

    def download_file_chunks(self, chunk_list, output_file_paths):
        for ((storage_name, cloud_file_id), output_file_path) in zip(chunk_list, output_file_paths):
            self.map_of_storage[storage_name].download_file(cloud_file_id, output_file_path)
