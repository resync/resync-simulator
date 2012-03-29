#!/usr/bin/env python

"""simulator.py: Simulates a ResourceSync SOURCE and fires change events"""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"

import time
import random

import util
import inventory


EVENT_TYPES = ["create", "update", "delete"]

DEFAULT_RESOURCES = 100
"""The default number of resources created at bootstrap"""
DEFAULT_FREQUENCY = 1
"""The default number of events fired per second"""
DEFAULT_EVENT_TYPES = EVENT_TYPES
"""The default types of events to be fired (ALL)"""
MAX_EVENTS = -1
"""The maximum number of events to be fired (-1 = infinite)"""

class Simulator:
    """This class simulates change events on a set/inventory of resources"""
    
    def __init__(self,
                resources = DEFAULT_RESOURCES,
                frequency = DEFAULT_FREQUENCY,
                event_types = DEFAULT_EVENT_TYPES):
        self.inventory = inventory.Inventory()
        self.resources = resources
        self.frequency = frequency
        self.event_types = event_types
        self.inventory.bootstrap(resources)
        print 'Initializing ChangeSimulator with %d resources, ' \
              'firing the following types of change events %d times ' \
              'per second: %s' % (resources, frequency, event_types)
    
    
    # Event firing
    
    def fire_create(self):
        """Creates a new resource"""
        self.inventory.create_resource()
        print "Firing create event at %s" % util.current_datetime()

    def fire_update(self, res_id):
        """Fires an update on a given resource"""
        self.inventory.update_resource(res_id)
        print "Firing update event on resource %s at %s" % (res_id,
            util.current_datetime())                                                
    
    def fire_delete(self, res_id):
        """Fires a delete on a given resource"""
        self.inventory.delete_resource(res_id)
        print "Firing delete event on resource %s at %s" % (res_id,
            util.current_datetime())                                                
    
    # Thread (TDB) control
    
    def run(self, max_events = MAX_EVENTS):
        """Start the simulator and fire random events"""
        no_events = 0
        sleep_time = round(float(1) / self.frequency, 2)
        while no_events < max_events:
            time.sleep(sleep_time)
            res_id = self.inventory.select_random_resource()
            event_type = random.choice(self.event_types)
            if event_type == "create":
                self.fire_create()
            elif event_type == "update":
                self.fire_update(res_id)
            elif event_type == "delete":
                self.fire_delete(res_id)
            else:
                print "Event type %s is not supported" % event_type
            no_events = no_events + 1
            
        
if __name__ == '__main__':
    simulator = Simulator(resources = 10, frequency = 3)
    print simulator.inventory
    simulator.run(10)
    print simulator.inventory
