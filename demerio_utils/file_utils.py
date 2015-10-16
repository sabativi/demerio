import os
import uuid
import shutil
import tempfile
from log import *


def generate_random_file_path():
    return tempfile.NamedTemporaryFile().name


def generate_random_file_name_in_dir(dirname):
    return tempfile.NamedTemporaryFile(dir=dirname).name


def generate_random_string():
    return str(uuid.uuid4())


def add_random_content_to_file(file_path):
    with open(file_path, 'a+') as f:
        f.write(str(uuid.uuid4()))


def create_new_file(file_path):
    with open(file_path, 'w+') as f:
        f.write("")


def create_random_file():
    return tempfile.mkstemp()[1]


def create_random_dir(dirname=None):
    if dirname is None:
        return tempfile.mkdtemp()
    else:
        return tempfile.mkdtemp(dir=dirname)


def create_new_file_in_dir(dirname):
    create_new_file(generate_random_file_name_in_dir(dirname))


def create_new_dir(dir_path):
    os.makedirs(dir_path)


def delete_dir(dir_path):
    shutil.rmtree(dir_path)


def move_dir(dir_path_src, dir_path_dest):
    os.renames(dir_path_src, dir_path_dest)


def copy_dir(src, dest):
    """mimic the cp -r command"""
    basename = os.path.split(src)[1]
    new_dest = os.path.join(dest, basename)
    shutil.copytree(src, new_dest)


def read_file(file_path):
    with open(file_path, 'r') as f:
        logger.debug("file content : %s", f.read())


def delete_file(file_path):
    try:
        os.remove(file_path)
    except OSError:
        pass


def copy_file(file_path_src, file_path_dest):
    shutil.copy(file_path_src, file_path_dest)


def move_file(file_path_src, file_path_dest):
    os.rename(file_path_src, file_path_dest)


def get_number_of_files_in_dir(dirname):
    return len(os.listdir(dirname))


def split_file_with_dir(file_path, dirname):
    return file_path.split(dirname + os.path.sep)[1]


def is_file_path(file_path):
    return os.path.isabs(file_path)


def get_size(file_path):
    try:
        return os.path.getsize(file_path)
    except:
        return 0


def count_files_recursively_in_dir(folder):
    total = 0
    for root, dirs, files in os.walk(folder):
        total += len(files)
    return total


def is_subdirectory(potential_subdirectory, expected_parent_directory):

    def os_path_split_asunder(path, debug=False):
        """
        http://stackoverflow.com/a/4580931/171094
        """
        parts = []
        while True:
            newpath, tail = os.path.split(path)
            if debug:
                print repr(path), (newpath, tail)
            if newpath == path:
                assert not tail
                if path:
                    parts.append(path)
                break
            parts.append(tail)
            path = newpath
        parts.reverse()
        return parts

    def _get_normalized_parts(path):
        return os_path_split_asunder(os.path.realpath(os.path.abspath(os.path.normpath(path))))

    # make absolute and handle symbolic links, split into components
    sub_parts = _get_normalized_parts(potential_subdirectory)
    parent_parts = _get_normalized_parts(expected_parent_directory)

    if len(parent_parts) > len(sub_parts):
        # a parent directory never has more path segments than its child
        return False

    # we expect the zip to end with the short path, which we know to be the parent
    return all(part1 == part2 for part1, part2 in zip(sub_parts, parent_parts))
