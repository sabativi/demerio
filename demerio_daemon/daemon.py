import time
from threading import Thread


class DemerioDaemon(Thread):
    """
    Daemon that listen to a repository at a given path and consume events
    with the handler
    """

    def __init__(self, event_handler, observer, path, should_exit, recursive=True):
        super(DemerioDaemon, self).__init__()
        self.event_handler = event_handler
        self.observer = observer
        self.should_exit = should_exit
        self.observer.schedule(self.event_handler, path, recursive)
        self.observer.start()

    def run(self):
        while not self.should_exit:
            time.sleep(1)
        self._stop()

    def _stop(self):
        self.observer.stop()

    def join(self):
        self.observer.join()
