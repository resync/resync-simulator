#!/usr/bin/env python
# encoding: utf-8
"""
changememory.py: A record of change events

Created by Bernhard Haslhofer on 2012-04-27.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

from observer import Observer

class ChangeMemory(Observer):
    """An abstract change memory implementation that doesn't do anything.
    ChangeMemory implementations can extend this class
    """
    
    def __init__(self, source):
        self.source = source
        source.register_observer(self)
        
    def bootstrap(self):
        """Bootstrap the Changememory; should be overridden by subclasses"""
        pass

# A dynamic in-memory change digest
class DynamicChangeSet(ChangeMemory):
    """A change memory that stores changes in an in-memory list"""

    def __init__(self, source, config):
        super(DynamicChangeSet, self).__init__(source)
        self.url = config['uri_path']
        self.max_changes = config['max_changes']
        self.config = config
        self.max_change_id = 0
        self.min_change_id = 0
        self._changes = []
        
    def notify(self, event):
        """Simply store a change in the in-memory list"""
        event.event_id = self.max_change_id + 1
        self.max_change_id = event.event_id
        if len(self._changes) >= self.max_changes:
            del self._changes[0]
            self.min_change_id = self._changes[0].event_id
        self._changes.append(event)
    
    @property
    def uri(self):
        """Returns the changememory's URI"""
        return self.source.base_uri + "/" + self.url
    
    @property
    def latest_event_id(self):
        """Returns the id of the latest change event"""
        return str(self.max_change_id)

    @property
    def first_event_id(self):
        """Returns the id of the first change event"""
        return str(self.min_change_id)

    def current_changeset_uri(self, event_id = None):
        """Constructs the URI of the current changeset."""
        
        if event_id is None:
            current_event_id = self.first_event_id
        else:
            current_event_id = event_id
        
        return self.source.base_uri + "/" + self.url + "/" + \
                current_event_id + "/diff"
    
    @property
    def next_changeset_uri(self):
        """Constructs the URI of the next changeset"""
        return self.source.base_uri + "/" + self.url + "/" + \
                self.latest_event_id + "/diff"
    
    @property
    def changes(self):
        """Returns all change events (sorted by event_id)"""
        return sorted(self._changes, key=lambda change: change.event_id)

    def changes_from(self, event_id):
        """Returns all changes starting from a certain event_id"""
        if not (self.min_change_id >= event_id and 
                event_id <= self.max_change_id):
            return None
        event_id = int(event_id)
        changes = [change for change in self._changes 
                            if change.event_id > event_id]
        return sorted(changes, key=lambda change: change.event_id)
    
    def knows_event_id(self, event_id = None):
        """Returns true if event_id is known (= stored)"""
        return ((self.min_change_id <= event_id) and
               (event_id <= self.max_change_id))
