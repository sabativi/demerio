from watchdog.events import LoggingEventHandler
from watchdog.events import PatternMatchingEventHandler
from demerio_utils.log import*

class MatchingHandler(PatternMatchingEventHandler):

    def __init__(self, ignore_patterns):
        PatternMatchingEventHandler.__init__(self, ignore_patterns=ignore_patterns)

    def on_moved(self, event):
        super(MatchingHandler, self).on_moved(event)

        what = 'directory' if event.is_directory else 'file'
        logger.info("Moved %s: from %s to %s", what, event.src_path,
                     event.dest_path)

    def on_created(self, event):
        super(MatchingHandler, self).on_created(event)

        what = 'directory' if event.is_directory else 'file'
        logger.info("Created %s: %s", what, event.src_path)

    def on_deleted(self, event):
        super(MatchingHandler, self).on_deleted(event)

        what = 'directory' if event.is_directory else 'file'
        logger.info("Deleted %s: %s", what, event.src_path)

    def on_modified(self, event):
        super(MatchingHandler, self).on_modified(event)

        what = 'directory' if event.is_directory else 'file'
        logger.info("Modified %s: %s", what, event.src_path)


class CountEventHandler(MatchingHandler):
    """Count number of event"""

    def __init__(self, ignore_patterns=None):
        super(CountEventHandler, self).__init__(ignore_patterns)
        self.list_of_events_received = []

    def on_any_event(self, event):
        super(CountEventHandler, self).on_any_event(event)
        logger.debug(event)
        self.list_of_events_received.append(event)

    def get_number_of_events_received(self):
        return len(self.list_of_events_received)

    def get_event_at(self, position):
        return self.list_of_events_received[position]

    def get_last_event(self):
        return self.get_event_at(-1)



