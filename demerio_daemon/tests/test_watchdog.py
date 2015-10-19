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


"Time to wait so that the system reveices the event"
WAIT_TIME = 2


class TestWatchDog(unittest.TestCase):

    def setUp(self):
        # Given
        self.observer = Observer()
        self.event_handler = CountEventHandler(ignore_patterns=["*.DS_Store"])
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

    @attr(slow=True)
    def test_on_created_with_ignore_pattern(self):
        # Given
        file_path = os.path.join(self.tempdir, ".DS_Store")

        # When
        self._start_observer()
        create_new_file(file_path)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 1)
        self.assertIsInstance(self.event_handler.get_event_at(0), DirModifiedEvent)

    @attr(slow=True)
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

    @attr(slow=True)
    def test_i_can_detect_a_directory_creation(self):
        # Given
        dir_path = os.path.join(self.tempdir, str(uuid.uuid4()))

        # When
        self._start_observer()
        create_new_dir(dir_path)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 2)
        self.assertIsInstance(self.event_handler.get_last_event(), DirCreatedEvent)

    @attr(slow=True)
    def test_i_can_detect_a_file_modification(self):
        # Given
        file_path = os.path.join(self.tempdir, str(uuid.uuid4()))
        create_new_file(file_path)
        time.sleep(WAIT_TIME)

        # When
        self._start_observer()
        add_random_content_to_file(file_path)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 1)
        self.assertIsInstance(self.event_handler.get_last_event(), FileModifiedEvent)

    @attr(slow=True)
    def test_i_can_detect_a_file_deletion(self):
        # Given
        file_path = os.path.join(self.tempdir, str(uuid.uuid4()))
        create_new_file(file_path)
        time.sleep(WAIT_TIME)

        # When
        self._start_observer()
        delete_file(file_path)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 2)
        self.assertIsInstance(self.event_handler.get_event_at(-2), FileDeletedEvent)

    @attr(slow=True)
    def test_i_can_detect_a_directory_move(self):
        # Given
        dir_path_src = os.path.join(self.tempdir, str(uuid.uuid4()))
        create_new_dir(dir_path_src)
        dir_path_dest = os.path.join(self.tempdir, str(uuid.uuid4()))
        time.sleep(WAIT_TIME)

        # When
        self._start_observer()
        move_dir(dir_path_src, dir_path_dest)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 2)
        self.assertIsInstance(self.event_handler.get_last_event(), DirMovedEvent)

    @attr(slow=True)
    def test_i_can_detect_a_directory_deletion(self):
        # Given
        dir_path = os.path.join(self.tempdir, str(uuid.uuid4()))
        create_new_dir(dir_path)
        time.sleep(WAIT_TIME)

        # When
        self._start_observer()
        delete_dir(dir_path)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 2)
        self.assertIsInstance(self.event_handler.get_event_at(-2), DirDeletedEvent)

    @attr(slow=True)
    def test_i_can_detect_a_file_move(self):
        # Given
        file_path_src = os.path.join(self.tempdir, str(uuid.uuid4()))
        create_new_file(file_path_src)
        file_path_dest = os.path.join(self.tempdir, str(uuid.uuid4()))
        time.sleep(WAIT_TIME)

        # When
        self._start_observer()
        move_file(file_path_src, file_path_dest)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 2)
        self.assertIsInstance(self.event_handler.get_event_at(-2), FileMovedEvent)

    @attr(slow=True)
    def test_i_can_detect_when_a_dir_is_moved(self):
        # Given
        dir_name = create_random_dir()
        create_new_file_in_dir(dir_name)
        create_new_file_in_dir(dir_name)

        # When
        self._start_observer()
        shutil.move(dir_name, self.tempdir)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 4)
        self.assertIsInstance(self.event_handler.get_event_at(0), FileCreatedEvent)
        self.assertIsInstance(self.event_handler.get_event_at(1), FileCreatedEvent)
        self.assertIsInstance(self.event_handler.get_event_at(2), DirModifiedEvent)
        self.assertIsInstance(self.event_handler.get_event_at(3), DirCreatedEvent)

    @attr(slow=True)
    def test_i_can_detect_when_a_dir_is_copied(self):
        # Given
        dir_name = create_random_dir()
        create_new_file_in_dir(dir_name)
        create_new_file_in_dir(dir_name)

        # When
        self._start_observer()
        copy_dir(dir_name, self.tempdir)
        time.sleep(WAIT_TIME)

        # Then
        self.assertEqual(self.event_handler.get_number_of_events_received(), 4)
        self.assertIsInstance(self.event_handler.get_event_at(0), FileCreatedEvent)
        self.assertIsInstance(self.event_handler.get_event_at(1), FileCreatedEvent)
        self.assertIsInstance(self.event_handler.get_event_at(2), DirModifiedEvent)
        self.assertIsInstance(self.event_handler.get_event_at(3), DirCreatedEvent)


if __name__ == '__main__':
    unittest.main()
