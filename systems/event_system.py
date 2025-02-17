import utility

class Event:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, listener):
        if not listener in self.subscribers:
            self.subscribers.append(listener)

    def unsubscribe(self, listener):
        self.subscribers.remove(listener)

    def emit(self, *args, **kwargs):
        for subscriber in self.subscribers:
            subscriber(*args, **kwargs)
