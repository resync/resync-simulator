#!/usr/bin/env python
# encoding: utf-8
"""
changememory.py: A collection of change memory implementations

Created by Bernhard Haslhofer on 2012-04-27.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

import tornado.web

from observer import Observer

class ChangeMemory(Observer):
    """An abstract change memory implementation that doesn't do anything.
    ChangeMemory implementations can extend this class
    """
    
    def __init__(self, source):
        self.source = source
        source.register_observer(self)

# A dynamic in-memory change digest
class DynamicChangeSet(ChangeMemory):
    """A change memory that stores changes in an in-memory list"""

    def __init__(self, source, config):
        super(DynamicChangeSet, self).__init__(source)
        self.url = config['uri_path']
        self.max_change_id = 0
        self._changes = []
        
    def notify(self, event):
        """Simply store a change in the in-memory list"""
        event.event_id = self.max_change_id
        self._changes.append(event)
        self.max_change_id = self.max_change_id + 1
    
    @property
    def changes(self):
        """Returns all change events (sorted by event_id)"""
        return sorted(self._changes, key=lambda change: change.event_id)

    def changes_from(self, event_id):
        """Returns all changes starting from a certain event_id"""
        event_id = int(event_id)
        changes = [change for change in self._changes if change.event_id > event_id]
        return sorted(changes, key=lambda change: change.event_id)
    
    @property
    def latest_event_id(self):
        """Returns the id of the latest change event"""
        if not self.has_change_events: return str(0)
        return str(len(self.changes) - 1)
        
    @property
    def first_event_id(self):
        """Returns the id of the first change event"""
        return str(0)
        
    @property
    def has_change_events(self):
        """Returns true if change events are availabe, false otherwise"""
        return bool(len(self.changes) > 0)
    
    @property
    def handlers(self):
        return [(r"%s" % self.url, 
                DynamicChangeSetHandler,
                dict(changememory = self)),
                (r"%s/([0-9]+)/diff" % self.url,
                DynamicChangeSetDiffHandler,
                dict(changememory = self)),
        ]
        

class DynamicChangeSetHandler(tornado.web.RequestHandler):
    """The HTTP request handler for the DynamicDigest"""

    def initialize(self, changememory):
        self.changememory = changememory
    
    @property
    def this_changeset_uri(self):
        """Constructs the URI of this (self) changeset"""
        return "http://" + self.request.host + self.changememory.url + "/" + \
                self.changememory.first_event_id + "/diff"
    
    @property
    def next_changeset_uri(self):
        """Constructs the URI of the next changeset"""
        return "http://" + self.request.host + self.changememory.url + "/" + \
                self.changememory.latest_event_id + "/diff"
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.render("changedigest.xml",
                    this_changeset_uri = self.this_changeset_uri,
                    next_changeset_uri = self.next_changeset_uri,
                    changes = self.changememory.changes)
                    

class DynamicChangeSetDiffHandler(DynamicChangeSetHandler):
    """The HTTP request handler for the DynamicDigest"""

    @property
    def this_changeset_uri(self):
        """Constructs the URI of this (self) changeset"""
        return "http://" + self.request.host + self.changememory.url + "/" + \
                self.event_id + "/diff"
    
    def get(self, event_id):
        self.event_id = event_id
        self.set_header("Content-Type", "application/xml")
        self.render("changedigest.xml",
                    this_changeset_uri = self.this_changeset_uri,
                    next_changeset_uri = self.next_changeset_uri,
                    changes = self.changememory.changes_from(event_id))