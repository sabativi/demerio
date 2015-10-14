import unittest
import tempfile
import uuid
import os
import time
from nose.plugins.attrib import attr

from demerio_daemon.observer import *
from demerio_daemon.handler import CountEventHandler
from demerio_utils.log import *
from watchdog.events import *
from demerio_utils.file_utils import *
from demerio_utils.deploy_platform import *
from distutils.dir_util import copy_tree


"Time to wait so that the system reveices the event"
WAIT_TIME = 2

def create_recursive_arborescence(base_dir, depth):
    prev_dir = base_dir
    for i in range(depth):
        prev_dir = create_random_dir(prev_dir)
    return prev_dir


class TestWatchDogLimits(unittest.TestCase):

    def setUp(self):
        # Given
        self.observer = Observer()
        self.event_handler = CountEventHandler()
        self.tempdir = os.path.realpath(tempfile.mkdtemp())

    def _start_observer(self):
        if is_darwin():
            time.sleep(10)
        self.observer.schedule(self.event_handler, self.tempdir, recursive=True)
        self.observer.start()

    def tearDown(self):
        self.observer.stop()
        # Clean
        delete_dir(self.tempdir)

    def recurive_arborescence_test(self):
        # Given
        last_dir_created = create_recursive_arborescence(self.tempdir, 80)

        # When
        self._start_observer()
        create_new_file_in_dir(last_dir_created)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 2)
        self.assertIsInstance(self.event_handler.get_event_at(-2), FileCreatedEvent)

if __name__ == '__main__':
    unittest.main()
