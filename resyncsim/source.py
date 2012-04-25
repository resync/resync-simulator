#!/usr/bin/env python
# encoding: utf-8
"""
source.py: A source contains a set of resources and changes over time.

Created by Bernhard Haslhofer on 2012-04-24.
Copyright (c) Cornell University. All rights reserved.
"""

import random

import time
from datetime import datetime
from collections import OrderedDict

from observer import Observable
from change import ChangeEvent

class Resource(object):
    """A resource has an identifier, a last modified date, and a payload of
    a certain size."""
    
    def __init__(self, id, payload_size):
        self.id = id
        self.lm_date = datetime.now().isoformat('T')
        self.payload_size = payload_size
        
    def update(self, new_payload_size):
        """Updates resource payload and last modified date"""
        self.lm_date = datetime.now().isoformat('T')
        self.payload_size = new_payload_size
        
    def uri(self, base_uri):
        """Constructs the resource uri by appending the internal id to a
        base URI (e.g., http://example.org/resources/)"""
        return base_uri + self.identifier
        
    def __str__(self):
        """Prints out the source's resources"""
        return "[%d | %s | %d]" % ( self.id, 
                                    self.lm_date, 
                                    self.payload_size)
    

class Source(Observable):
    """A source contains a list of resources and changes over time"""
    
    def __init__(self, config):
        """Initalize the source"""
        super(Source, self).__init__()
        self.number_of_resources = config['number_of_resources']
        self.average_payload = config['average_payload']
        self.change_frequency = config['change_frequency']
        self.event_types = config['event_types']
        self.max_events = config['max_events']
        
        self.max_res_id = 0
        self.resources = {} # stores resources by id | resource_object
        self.bootstrap()
        
    def bootstrap(self):
        """Bootstrap the source with a set of resources"""
        print "*** Bootstrapping source with %d resources and an average " \
                "resource payload of %d bytes ***" \
                 % (self.number_of_resources, self.average_payload)
        
        for i in range(self.number_of_resources):
            self.create_resource(notify_observers = False)
    
    def select_random_resource(self):
        """Selects a random resource"""
        if len(self.resources.keys()) > 0:
            random_res_id = random.choice(self.resources.keys())
            return self.resources[random_res_id]
        else:
            return None
    
    def create_resource(self, notify_observers = True):
        """Create a new resource, add it to the source, notify observers."""
        res_id = self.max_res_id
        self.max_res_id += 1
        res = Resource(
            id = res_id,
            payload_size = random.randint(0, self.average_payload)
        )
        self.resources[res_id] = res
        if notify_observers:
            event = ChangeEvent("CREATE", res)
            self.notify_observers(event)
        
    def update_resource(self, res):
        """Update a resource, notify observers."""
        res = self.resources[res.id]
        res.update(random.randint(0, self.average_payload))
        event = ChangeEvent("UPDATE", res)
        self.notify_observers(event)

    def delete_resource(self, res):
        """Delete a given resource, notify observers."""
        res = self.resources[res.id]
        del self.resources[res.id]
        res.lm_date = datetime.now().isoformat('T')
        event = ChangeEvent("DELETE", res)
        self.notify_observers(event)
    
    def simulate_changes(self):
        """Simulate changing resources in the source"""
        print "*** Starting change simulation with frequency %s and event " \
                "types %s ***" \
                 % (str(round(self.change_frequency, 2)), self.event_types)
        no_events = 0
        sleep_time = round(float(1) / self.change_frequency, 2)
        while no_events != self.max_events:
            time.sleep(sleep_time)
            event_type = random.choice(self.event_types)
            if event_type == "create":
                self.create_resource()
            elif event_type == "update" or event_type == "delete":
                res = self.select_random_resource()
                if res is None: 
                    print "The repository is empty"
                    no_events = no_events + 1                    
                    continue
                if event_type == "update":
                    self.update_resource(res)
                elif event_type == "delete":
                    self.delete_resource(res)
                    
            else:
                print "Event type %s is not supported" % event_type
            no_events = no_events + 1
        
        print "*** Finished change simulation ***"
    
    def __str__(self):
        """Prints out the source's resources"""
        return '\n'.join([str(r) for (id, r) in self.resources.items()])

        
# run standalone for testing purposes
if __name__ == '__main__':
    config = dict(
        number_of_resources = 10,
        change_frequency = 2,
        average_payload = 100,
        event_types = ['create', 'update', 'delete'],
        max_events = 5)
    source = Source(config)
    
    print source

    try:
        source.simulate_changes()
    except KeyboardInterrupt:
        print "Exiting gracefully..."    

    print source