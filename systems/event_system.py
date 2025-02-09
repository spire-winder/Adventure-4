
class Event:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, listener):
        self.subscribers.append(listener)

    def emit(self, *args, **kwargs):
        for subscriber in self.subscribers:
            subscriber(*args, **kwargs)
