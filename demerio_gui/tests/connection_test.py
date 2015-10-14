import unittest
from nose.plugins.attrib import attr
from demerio_gui.connection_handler import ConnectionHandler
from mock import MagicMock

class ConnectionHandlerTest(unittest.TestCase):

    def test_internet_is_None_by_default(self):
        # Given
        connection_handler = ConnectionHandler()

        # Then
        self.assertIsNone(connection_handler.internet_ok)

    def test_internet_is_ok_after_first_check(self):
        # Given
        connection_handler = ConnectionHandler()

        # When
        connection_handler.update()

        # Then
        self.assertTrue(connection_handler.internet_ok)

    def test_when_no_internet(self):
        # Given
        connection_handler = ConnectionHandler()
        connection_handler.check_internet_call = MagicMock(side_effect=Exception('HTTP Error'))

        # When
        connection_handler.update()

        # Then
        self.assertFalse(connection_handler.internet_ok)

    def test_have_internet_again(self):
        # Given
        connection_handler = ConnectionHandler()
        connection_handler.internet_ok = False

        # When
        connection_handler.update()

        # Then
        self.assertTrue(connection_handler.internet_ok)

