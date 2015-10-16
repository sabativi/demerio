import unittest
import random
import shutil
import tempfile
import os

import demerio_split.fec as fec


KB = 1024
MB = 1024*KB
GB = 1024*MB


class TestFileFec(object):

    def _help_test_filefec(self, size_in_bytes, k, m, numshs):

        tempdir = tempfile.mkdtemp()

        expected_output = os.urandom(size_in_bytes)

        file_fec = fec.FileFec(k, m)
        try:
            # encode the input_file
            tempf = file(os.path.join(tempdir, "input-test"), 'w+b')
            tempf.write(expected_output)
            tempf.flush()
            tempf.seek(0)

            fns = file_fec.encode_file(tempf, tempdir)

            # remove some parts
            del fns[numshs:]
            random.shuffle(fns)

            # decode from the share files
            chunks = [open(fn, "rb") for fn in fns]

            output_path = os.path.join(tempdir, 'output-test')

            file_fec.decode_files(output_path, chunks)

            actual_output = open(output_path, "rb").read()
            assert actual_output == expected_output
        finally:
            shutil.rmtree(tempdir)

    def test_filefec_with_binary_file(self):
        for i in range(100):
            m = random.randint(3, 6)
            k = random.randint(1, m - 1)
            numshs = random.randint(k + 1, m)
            size = random.randint(1, 100)
            yield self._help_test_filefec, size * KB, k, m, numshs


if __name__ == "__main__":
    unittest.main()
