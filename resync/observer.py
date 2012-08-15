"""observer.py: A collection of utils for implementing the Observer pattern.

See: http://en.wikipedia.org/wiki/Observer_pattern

Created by Bernhard Haslhofer on 2012-04-24.
Copyright 2012, ResourceSync.org. All rights reserved.

"""

class Observer(object):
    """Observers are informed about events"""
    
    def name(self):
        return self.__class__.__name__
    
    def notify(self, event):
        pass


class Observable(object):
    """Observable subjects issue events and nofiy registered Observers"""
    
    def __init__(self):
        self.observers = []
    
    def register_observer(self, observer):
        self.observers.append(observer)
        
    def notify_observers(self, event):
        """Notifies observers about change events"""
        for observer in self.observers:
            observer.notify(event)
        