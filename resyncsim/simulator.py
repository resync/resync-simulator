#!/usr/bin/env python
# encoding: utf-8
"""
simulator.py: Simulates changes on resources in a given inventory.

Created by Bernhard Haslhofer on 2012-04-02.
Copyright (c) 2012 resourcesync.org. All rights reserved.
"""

import time
import random

import util
from inventory import Inventory
from observer import Observable

# TODO: find out how to properly handle enums in python
EVENT_TYPES = ["create", "update", "delete"]
"""The types of events to be fired"""
DEFAULT_FREQUENCY = 1
"""The default number of events fired per second"""
DEFAULT_EVENT_TYPES = EVENT_TYPES
"""The default types of events to be fired (ALL)"""
DEFAULT_MAX_EVENTS = -1
"""The default number of events to be fired (-1 = infinite)"""

class ChangeEvent(object):
    """A Change Event carries a type, a timestamp and the affected resource"""
    
    def __init__(self, event_type, timestamp, resource):
        self.event_type = event_type
        self.timestamp = timestamp
        self.resource = resource
        
    def __str__(self):
        return "[" + self.event_type + "|" + \
                     str(self.resource['id']) + "|"  + \
                     self.timestamp + "]"


class Simulator(Observable):
    """This class simulates change events on a set/inventory of resources"""
    
    def __init__(self, inventory,
                frequency = DEFAULT_FREQUENCY,
                event_types = DEFAULT_EVENT_TYPES,
                max_events = DEFAULT_MAX_EVENTS,
                debug = False):

        super(Simulator, self).__init__()
        self.max_events = max_events
        self.inventory = inventory
        self.frequency = frequency
        self.event_types = event_types
        self.debug = debug
        
    # Event firing
    
    def fire_create(self):
        """Create a new resource and notify observers"""
        res = self.inventory.create_resource()
        if self.debug is True:
            print "Created resource %s" % res
        event = ChangeEvent("create", util.current_datetime(), res)
        self.notify_observers(event)

    def fire_update(self, res_id):
        """Fires an update on a given resource and notify observers"""
        res = self.inventory.update_resource(res_id)
        if self.debug is True:
            print "Updated resource %s" % res
        event = ChangeEvent("update", util.current_datetime(), res)
        self.notify_observers(event)
    
    def fire_delete(self, res_id):
        """Fires a delete on a given resource and notify observers"""
        res = self.inventory.delete_resource(res_id)
        if self.debug is True:
            print "Deleted resource %s" % res
        event = ChangeEvent("delete", util.current_datetime(), res)
        self.notify_observers(event)
    
    def run(self):
        print "*** Starting change simulation with frequency %s and event " \
                "types %s ***" \
                 % (str(round(self.frequency, 2)), self.event_types)
        no_events = 0
        sleep_time = round(float(1) / self.frequency, 2)
        while no_events != self.max_events:
            time.sleep(sleep_time)
            event_type = random.choice(self.event_types)
            if event_type == "create":
                self.fire_create()
            elif event_type == "update" or event_type == "delete":
                res_id = self.inventory.select_random_resource()
                if res_id is None: print "No more resources"; break 
                if event_type == "update":
                    self.fire_update(res_id)
                elif event_type == "delete":
                    self.fire_delete(res_id)
            else:
                print "Event type %s is not supported" % event_type
            no_events = no_events + 1


if __name__ == '__main__':
    inventory = Inventory(5)
    print inventory
    simulator = Simulator(frequency = 1, inventory = inventory, 
                            max_events = 5,
                            debug = True)
    try:
        simulator.run()
    except KeyboardInterrupt:
        print "Exiting gracefully..."
    
    print inventory