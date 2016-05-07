"""observer.py: A collection of utils for implementing the Observer pattern.

See: http://en.wikipedia.org/wiki/Observer_pattern

Created by Bernhard Haslhofer on 2012-04-24.
Copyright 2012, ResourceSync.org. All rights reserved.
"""


class Observer(object):
    """Observers are informed about events."""

    def name(self):
        """Name of observer class."""
        return self.__class__.__name__

    def notify(self, event):
        """Notify observer."""
        pass


class Observable(object):
    """Observable subjects issue events and nofiy registered Observers."""

    def __init__(self):
        """Initialize with empty list of observers."""
        self.observers = []

    def register_observer(self, observer):
        """Register and observer."""
        self.observers.append(observer)

    def notify_observers(self, event):
        """Notify observers about change events."""
        for observer in self.observers:
            observer.notify(event)
