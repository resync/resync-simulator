#!/usr/bin/env python

"""simulator.py: Simulates a ResourceSync SOURCE and fires change events"""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"

import time
import random

import util
import inventory
from observer import Observable

# TODO: find out how proper enum handling works in python
EVENT_TYPES = ["create", "update", "delete"]

DEFAULT_RESOURCES = 100
"""The default number of resources created at bootstrap"""
DEFAULT_FREQUENCY = 1
"""The default number of events fired per second"""
DEFAULT_EVENT_TYPES = EVENT_TYPES
"""The default types of events to be fired (ALL)"""

MAX_EVENTS = -1
"""The maximum number of events to be fired (-1 = infinite)"""

class ChangeEvent(object):
    """A Change Event carries a type, a timestamp and the affected resource"""
    
    def __init__(self, event_type, timestamp, resource):
        self.event_type = event_type
        self.timestamp = timestamp
        self.resource = resource
        
    def __str__(self):
        return "[" + self.event_type + "|" + \
                     str(self.resource['rid']) + "|"  + \
                     self.timestamp + "]"


class Simulator(Observable):
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
        super(Simulator, self).__init__()
        print 'Initializing ResourceSync ChangeSimulator:\n' \
                '\t# seed resources: %d\n' \
                '\t# changes per second: %d\n' \
                '\tevent types: %s' \
                % (resources, frequency, event_types)
    
    # Event firing
    
    def fire_create(self):
        """Create a new resource and notify observers"""
        res = self.inventory.create_resource()
        event = ChangeEvent("create", util.current_datetime(), res)
        self.notify_observers(event)

    def fire_update(self, res_id):
        """Fires an update on a given resource and notify observers"""
        res = self.inventory.update_resource(res_id)
        event = ChangeEvent("update", util.current_datetime(), res)
        self.notify_observers(event)
    
    def fire_delete(self, res_id):
        """Fires a delete on a given resource and notify observers"""
        res = self.inventory.delete_resource(res_id)
        event = ChangeEvent("delete", util.current_datetime(), res)
        self.notify_observers(event)
    
    # Thread control
    # TODO: do we need to implement "real" threading?
    
    def run(self, max_events = MAX_EVENTS):
        """Start the simulator and fire random events"""
        print "Starting simulation...."
        no_events = 0
        sleep_time = round(float(1) / self.frequency, 2)
        while no_events != max_events:
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
