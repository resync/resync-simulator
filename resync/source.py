#!/usr/bin/env python
# encoding: utf-8
"""
source.py: A source contains a set of resources and changes over time.

Created by Bernhard Haslhofer on 2012-04-24.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

import random
import hashlib

import time
from datetime import datetime
from collections import OrderedDict

from observer import Observable
from change import ChangeEvent
from resource import Resource

class Source(Observable):
    """A source contains a list of resources and changes over time"""
    
    def __init__(self, config):
        """Initalize the source"""
        super(Source, self).__init__()
        self.config = config
        self.max_res_id = 0
        self.resources = {} # stores resources by id | resource_object
        self.bootstrap()
        
    def bootstrap(self):
        """Bootstrap the source with a set of resources"""
        print "*** Bootstrapping source with %d resources and an average " \
                "resource payload of %d bytes ***" \
                 % (self.config['number_of_resources'],
                    self.config['average_payload'])
        
        for i in range(self.config['number_of_resources']):
            self.create_resource(notify_observers = False)
    
    
    def random_resources(self, number = 1):
        "Return a random set of resources, at most all resources"
        if number > len(self.resources):
            number = len(self.resources)
        return random.sample(self.resources.values(), number)

    def random_resource(self):
        "Selects a single random resource"
        rand_res = self.random_resources(1)
        if len(rand_res) == 1:
            return rand_res[0]
        else:
            raise "Unexpected empty result set when selecting random resource"
    
    def create_resource(self, notify_observers = True):
        """Create a new resource, add it to the source, notify observers."""
        res_id = self.max_res_id
        self.max_res_id += 1
        res = Resource(
            id = res_id,
            size = random.randint(0, self.config['average_payload'])
        )
        self.resources[res_id] = res
        if notify_observers:
            event = ChangeEvent("CREATE", res)
            self.notify_observers(event)
        
    def update_resource(self, res):
        """Update a resource, notify observers."""
        res = self.resources[res.id]
        res.update(random.randint(0, self.config['average_payload']))
        event = ChangeEvent("UPDATE", res)
        self.notify_observers(event)

    def delete_resource(self, res):
        """Delete a given resource, notify observers."""
        res = self.resources[res.id]
        del self.resources[res.id]
        res.lastmod = datetime.now().isoformat('T')
        event = ChangeEvent("DELETE", res)
        self.notify_observers(event)
    
    def simulate_changes(self):
        """Simulate changing resources in the source"""
        print "*** Starting change simulation with frequency %s and event " \
                "types %s ***" \
                 % (str(round(self.config['change_frequency'], 2)), 
                    self.config['event_types'])
        no_events = 0
        sleep_time = round(float(1) / self.config['change_frequency'], 2)
        while no_events != self.config['max_events']:
            time.sleep(sleep_time)
            event_type = random.choice(self.config['event_types'])
            if event_type == "create":
                self.create_resource()
            elif event_type == "update" or event_type == "delete":
                res = self.random_resource()
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