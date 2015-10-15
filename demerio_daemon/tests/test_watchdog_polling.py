import unittest
import tempfile
import uuid
import os
import time
from nose.plugins.attrib import attr

from demerio_daemon.handler import CountEventHandler
from demerio_utils.log import *
from watchdog.events import *
from demerio_utils.file_utils import *
from demerio_utils.deploy_platform import *
from watchdog.observers.polling import PollingObserver as Observer


"Time to wait so that the system reveices the event"
WAIT_TIME = 2


class TestWatchDog(unittest.TestCase):

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

    @attr(slow=True)
    def test_watching_an_empty_diretory_just_created(self):
        # When
        self._start_observer()

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 0)

    @attr(current=True)
    def test_i_can_detect_a_file_creation(self):
        # Given
        file_path = os.path.join(self.tempdir, str(uuid.uuid4()))

        # When
        self._start_observer()
        create_new_file(file_path)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 2)
        self.assertIsInstance(self.event_handler.get_event_at(-2), FileCreatedEvent)
