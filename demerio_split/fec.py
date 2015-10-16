import zfec
import glob
import os
import tempfile
from demerio_utils.file_utils import *
from striping import Striping

SUFFIX = ".demerio"


class FileFec(Striping):

    def __init__(self, k, m):
        super(FileFec, self).__init__(k, m)

    def encode_path_in_dir(self, input_path, temp_dir):
        with open(input_path, "rb") as f:
            parts = self.encode_file(f, temp_dir)
        return parts

    def encode_path(self, input_file):
        temp_dir = tempfile.mkdtemp()
        self.encode_path_in_dir(input_file, temp_dir)

    def encode_file(self, input_file, output_dir, suffix=SUFFIX):
        fsize = os.stat(input_file.name).st_size
        basename = generate_random_string()  # NOTE: is this really unique
        zfec.filefec.encode_to_files(input_file, fsize, output_dir, basename, self.k, self.m, suffix, True, True)
        return glob.glob(output_dir + '/*' + suffix)

    def decode_path(self, output_path, chunks_path):
        chunks_file = [open(chunk_path) for chunk_path in chunks_path]
        self.decode_files(output_path, chunks_file)

    def decode_files(self, output_path, chunks_file):
        with open(output_path, 'w+b') as outf:
            zfec.filefec.decode_from_files(outf, chunks_file)
