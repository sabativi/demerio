from watchdog.events import LoggingEventHandler

class CountEventHandler(LoggingEventHandler):
    """Count number of event"""

    def __init__(self):
        super(CountEventHandler, self).__init__()
        self.list_of_events_received = []

    def on_any_event(self, event):
        super(CountEventHandler, self).on_any_event(event)
        self.list_of_events_received.append(event)

    def get_number_of_events_received(self):
        return len(self.list_of_events_received)

    def get_event_at(self, position):
        return self.list_of_events_received[position]

    def get_last_event(self):
        return self.get_event_at(-1)


class BaseHandler(LoggingEventHandler):

    def on_created_event(self, event):
        pass
