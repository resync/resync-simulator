#!/usr/bin/env python

"""simulator.py: Simulates a ResourceSync data source and fires events
according to a set of parameters."""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"

from datetime import datetime
import time
import random
import pprint


class EventType:
    """Enumeration of supported event types"""
    CREATE, UPDATE, DELETE = range(3)
    ALL = [CREATE, UPDATE, DELETE]


class Resource:
    """A Web Resource"""
    def __init__(self, id, payload):
        self.id = id
        self.payload = payload


DEFAULT_RESOURCES = 100
DEFAULT_FREQUENCY = 1
DEFAULT_EVENT_TYPES = EventType.ALL

MAX_PAYLOAD_SIZE = 500
MAX_EVENTS = -1 # Limit the number of events or run infinite (-1)


class Simulator:
    """This class simulates ResourceSync changes on a set of resources"""
    
    def __init__(self,
                resources = DEFAULT_RESOURCES,
                frequency = DEFAULT_FREQUENCY,
                event_types = DEFAULT_EVENT_TYPES):
        self.resources = resources
        self.frequency = frequency
        self.event_types = event_types
        print 'Initializing ChangeSimulator with %d resources, ' \
              'firing the following types of change events %d times ' \
              'per second: %s' % (self.resources, self.frequency,
                                  self.event_types)
        self.init_inventory()
    
    
    # Repository functions
    
    def init_inventory(self):
        """Initializes the resource inventory at startup time"""
        self.current_resources = {} # holds current inventory state (key = id)
        for i in range(self.resources):
            self.current_resources[i] = dict(
                                            lm_date = self.current_datetime(),
                                            payload = self.generate_payload())
        self.deleted_resources = {} # keeps deletion history
        self.updated_resources = {} # keeps update history
        
    def print_inventory(self):
        """Prints out the current simulator inventory as string"""
        return pprint.pprint(self.current_resources)
        
    def print_deletion_history(self):
        """Prints the history of deleted resources as string"""
        return pprint.pprint(self.deleted_resources)

    def print_update_history(self):
        """Prints the history of updated resources as string"""
        return pprint.pprint(self.deleted_resources)

    

    # Helper functions
    
    def current_datetime(self):
        """Returns a nicely formatted date time string"""
        return datetime.now().isoformat('T')
    
    def generate_payload(self):
        """Generates random payload size between 0 and MAX_PAYLOAD_SIZE"""
        return random.randint(0, MAX_PAYLOAD_SIZE)
    
    
    # Event firing
    
    def fire_update(self):
        """Fires an update on a randomly chosen resource"""
        print "Firing update event at %s" % self.current_datetime()                                                
    
    def fire_delete(self):
        """Fires a delete on a randomly chosen resource"""
        print "Firing delete event at %s" % self.current_datetime()
        #del_resource = 

    def fire_create(self):
        """Creates a new resource"""
        print "Firing create event at %s" % self.current_datetime()

    
    # Thread (tbd) control functions
    
    def run(self, max_events = MAX_EVENTS):
        """Start the simulator and fire random events"""
        no_events = 0
        sleep_time = round(float(1) / self.frequency, 2)
        while no_events < max_events:
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
            no_events = no_events + 1
            
        
if __name__ == '__main__':
    simulator = Simulator(resources = 10, frequency = 3)
    simulator.print_inventory()
    simulator.run(10)
    simulator.print_inventory()
    simulator.print_deletion_history()
    simulator.print_update_history()

