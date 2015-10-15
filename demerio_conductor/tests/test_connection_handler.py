import unittest
from nose.plugins.attrib import attr
from demerio_conductor.connection_handler import ConnectionHandler
from mock import MagicMock

fake_params = (3, 5)

class ConnectionHandlerTest(unittest.TestCase):

    def test_internet_is_None_by_default(self):
        # Given
        connection_handler = ConnectionHandler(*fake_params)

        # Then
        self.assertIsNone(connection_handler.internet_ok)

    def test_internet_is_ok_after_first_check(self):
        # Given
        connection_handler = ConnectionHandler(*fake_params)

        # When
        connection_handler.update()

        # Then
        self.assertTrue(connection_handler.internet_ok)

    def test_when_no_internet(self):
        # Given
        connection_handler = ConnectionHandler(*fake_params)
        connection_handler.check_internet_call = MagicMock(side_effect=Exception('HTTP Error'))

        # When
        connection_handler.update()

        # Then
        self.assertFalse(connection_handler.internet_ok)

    def test_have_internet_again(self):
        # Given
        connection_handler = ConnectionHandler(*fake_params)
        connection_handler.internet_ok = False

        # When
        connection_handler.update()

        # Then
        self.assertTrue(connection_handler.internet_ok)

