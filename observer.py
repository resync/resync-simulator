"""observer.py: A collection of utils for implementing the Observer pattern.

See: http://en.wikipedia.org/wiki/Observer_pattern

"""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"

class Observer(object):
    """Observers are informed about events"""
    
    def notify(self, event):
        pass


class Observable(object):
    """Observable subjects issue events and nofiy registered Observers"""
    
    def __init__(self):
        self.observers = []
    
    def register_observer(self, observer):
        print "Registering an observer"
        self.observers.append(observer)
        
    def notify_observers(self, event):
        for observer in self.observers:
            observer.notify(event)
        