#!/usr/bin/env python
# encoding: utf-8
"""
source.py: A source contains a set of resources and changes over time.

Created by Bernhard Haslhofer on 2012-04-24.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

import random
import pprint

import time
from urlparse import urlparse
from posixpath import basename

from observer import Observable
from change import ChangeEvent
from resource import Resource, compute_md5

class Source(Observable):
    """A source contains a list of resources and changes over time"""
    
    def __init__(self, config):
        """Initalize the source"""
        super(Source, self).__init__()
        self.config = config
        self.max_res_id = 0
        self._repository = {} # stores resources by {id | {timestamp | size} }
        self.bootstrap()
        
    def bootstrap(self):
        """Bootstrap the source with a set of resources"""
        print "*** Bootstrapping source with %d resources and an average " \
                "resource payload of %d bytes ***" \
                 % (self.config['number_of_resources'],
                    self.config['average_payload'])
        
        for i in range(self.config['number_of_resources']):
            self.create_resource(notify_observers = False)
    
    def resource(self, res_id):
        """Generate a resource object from internal resource repository"""
        uri = "http://localhost:8888/resource/" + str(res_id)
        timestamp = self._repository[res_id]['timestamp']
        size = self._repository[res_id]['size']
        md5 = compute_md5(self.generate_dummy_payload(res_id, size))
        return Resource(uri = uri, timestamp = timestamp, size = size,
                        md5 = md5)
    
    def extract_res_id(self, uri):
        """Extracts the internal res_id identifier from a URI"""
        parse_object = urlparse(self.uri)
        return basename(parse_object.path)
    
    def generate_dummy_payload(self, res_id, size):
        """Generates dummy payload by repeating res_id x size times"""
        no_repetitions = size / len(str(res_id))
        content = "".join([str(res_id) for x in range(no_repetitions)])
        no_fill_chars = size % len(str(res_id))
        fillchars = "".join(["x" for x in range(no_fill_chars)])
        return content + fillchars
    
    def random_resources(self, number = 1):
        "Return a random set of resources, at most all resources"
        if number > len(self._repository):
            number = len(self._repository)
        rand_res_ids = random.sample(self._repository.keys(), number)
        return [self.resource(res_id) for res_id in rand_res_ids]

    def random_resource(self):
        "Selects a single random resource"
        rand_res = self.random_resources(1)
        if len(rand_res) == 1:
            return rand_res[0]
        else:
            raise "Unexpected empty result set when selecting random resource"
    
    def create_resource(self, res_id = None, notify_observers = True):
        """Create a new resource, add it to the source, notify observers."""
        if res_id == None:
            res_id = self.max_res_id
            self.max_res_id += 1
        timestamp = time.time()
        size = random.randint(0, self.config['average_payload'])
        self._repository[res_id] = {'timestamp': timestamp, 'size': size}
        if notify_observers:
            event = ChangeEvent("CREATE", self.resource(res_id))
            self.notify_observers(event)
        
    def update_resource(self, res_id):
        """Update a resource, notify observers."""
        self.delete_resource(res_id, notify_observers = False)
        res = self.create_resource(res_id, notify_observers = False)
        event = ChangeEvent("UPDATE", self.resource(res_id))
        self.notify_observers(event)

    def delete_resource(self, res_id, notify_observers = True):
        """Delete a given resource, notify observers."""
        res = self.resource(res_id)
        del self._repository[res_id]
        res.timestamp = time.time()
        if notify_observers:
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
                if len(self._repository.keys()) > 0:
                    res_id = random.sample(self._repository.keys(), 1)[0]
                else:
                    res_id = None
                if res_id is None: 
                    print "The repository is empty"
                    no_events = no_events + 1                    
                    continue
                if event_type == "update":
                    self.update_resource(res_id)
                elif event_type == "delete":
                    self.delete_resource(res_id)
                    
            else:
                print "Event type %s is not supported" % event_type
            no_events = no_events + 1
        
        print "*** Finished change simulation ***"
    
    def __str__(self):
        """Prints out the source's resources"""
        return pprint.pformat(self._repository)

        
# run standalone for testing purposes
if __name__ == '__main__':
    config = dict(
        number_of_resources = 10,
        change_frequency = 1,
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