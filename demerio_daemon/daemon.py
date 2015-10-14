import time
from threading import Thread


class DemerioDaemon(Thread):
    """
    Daemon that listen to a repository at a given path and consume events
    with the handler
    """

    def __init__(self, event_handler, observer, path, recursive=True):
        super(DemerioDaemon, self).__init__()
        self.event_handler = event_handler
        self.observer = observer
        self.observer.schedule(self.event_handler, path, recursive)
        self.observer.start()

    def run(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._stop()

    def _stop(self):
        self.observer.stop()
