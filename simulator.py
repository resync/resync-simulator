#!/usr/bin/env python

"""simulator.py: Simulates a ResourceSync data source and fires events
according to a set of parameters."""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"

from datetime import datetime
import time
import random


class EventType:
    """Enumeration of supported event types"""
    CREATE, UPDATE, DELETE = range(3)
    ALL = [CREATE, UPDATE, DELETE]


class Resource:
    """A Web Resource"""
    def __init__(self, id, payload):
        self.id = id
        self.payload = payload


DEFAULT_RESOURCES = 1000
DEFAULT_FREQUENCY = 1
DEFAULT_EVENT_TYPES = EventType.ALL


class Simulator:
    """This class simulates ResourceSync changes on a set of resources"""
    
    def __init__(self,
                resources = DEFAULT_RESOURCES,
                frequency = DEFAULT_FREQUENCY,
                event_types = DEFAULT_EVENT_TYPES):
        self.resources = resources
        self.frequency = frequency
        self.event_types = event_types
        self.deleted_resources = [] # stores IDs of delete resources
        self.updated_resources = [] # keeps track of resource updates
        print 'Setting up ChangeSimulator with %d resources, ' \
              'firing the following types of change events %d times ' \
              'per second: %s' % (self.resources, self.frequency,
                                  self.event_types)

    def fire_update(self):
        """Fires an update on a randomly chosen resource"""
        print "Firing update event at %s" % self.current_datetime()                                                
    
    def fire_delete(self):
        """Fires a delete on a randomly chosen resource"""
        print "Firing delete event at %s" % self.current_datetime()

    def fire_create(self):
        """Creates a new resource"""
        print "Firing create event at %s" % self.current_datetime()

    def current_datetime(self):
        return datetime.now().isoformat('T')
    
    def run(self):
        """Start the simulator and fire random events"""
        sleep_time = round(float(1) / self.frequency, 2)
        while True:
            time.sleep(sleep_time)
            event_type = random.choice(self.event_types)
            if event_type == EventType.CREATE:
                self.fire_create()
            elif event_type == EventType.UPDATE:
                self.fire_update()
            elif event_type == EventType.DELETE:
                self.fire_delete()
            else:
                print "Event type %s is not supported" % event_type
            
        
if __name__ == '__main__':
    simulator = Simulator(frequency = 2)
    #simulator.enable_Web(true)
    simulator.run()
