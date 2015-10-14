from abc import ABCMeta
from abc import abstractmethod


class DemerioSplitError(Exception):
    pass

class Striping():
    """
    Split data into m blocks any k of which
    are sufficients to reconstruct the input data
    """

    __metaclass__=ABCMeta

    def __init__(self, k, m):
        self.k = k
        self.m = m

    @abstractmethod
    def encode_path_in_dir(self, input_path, temp_dir):
        pass

    @abstractmethod
    def decode_path(self, output_path, chunks):
        pass
