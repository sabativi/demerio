from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler

import logging
logging.basicConfig(level=logging.DEBUG)

class MatchingHandler(PatternMatchingEventHandler):

    def __init__(self, ignore_patterns):
        PatternMatchingEventHandler.__init__(self, ignore_patterns=ignore_patterns)


class CountEventHandler(MatchingHandler):
    """Count number of event"""

    def __init__(self, ignore_patterns=None):
        super(CountEventHandler, self).__init__(ignore_patterns)
        self.list_of_events_received = []

    def on_any_event(self, event):
        super(CountEventHandler, self).on_any_event(event)
        logging.debug(event)
        self.list_of_events_received.append(event)

    def get_number_of_events_received(self):
        return len(self.list_of_events_received)

    def get_event_at(self, position):
        return self.list_of_events_received[position]

    def get_last_event(self):
        return self.get_event_at(-1)



