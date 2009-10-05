class Lock(object):
    """Lock class to use for event collision prevention"""
    def __init__(self, exc_class):
        self.lock = False
        self.exc_class = exc_class

    def lock(self):
        if self.lock:
            raise self.exc_class()
        self.lock = True

    def unlock(self):
        if not self.lock:
            raise self.exc_class()
        self.lock = False
