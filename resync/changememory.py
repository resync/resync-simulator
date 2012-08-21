#!/usr/bin/env python
# encoding: utf-8
"""
changememory.py: A record of change events

Created by Bernhard Haslhofer on 2012-04-27.
Copyright 2012, ResourceSync.org. All rights reserved.
"""
import logging

from resync.observer import Observer
from resync.changeset import ChangeSet

class ChangeMemory(Observer):
    """An abstract change memory implementation that doesn't do anything.
    ChangeMemory implementations can extend this class
    """
    
    def __init__(self, source):
        self.source = source
        source.register_observer(self)
        self.logger = logging.getLogger('changememory')
        
    def bootstrap(self):
        """Bootstrap the Changememory; should be overridden by subclasses"""
        pass

# A dynamic in-memory change set
class DynamicChangeSet(ChangeMemory):
    """A change memory that stores changes in an in-memory list"""

    def __init__(self, source, config):
        super(DynamicChangeSet, self).__init__(source)
        self.uri_path = config['uri_path']
        self.max_changes = config['max_changes']
        self.config = config
        self.latest_change_id = 0
        self.first_change_id = 0
        self.changes = [] # stores change events; sorted by event id
        
    @property
    def base_uri(self):
        """Returns the changememory's URI"""
        return self.source.base_uri + "/" + self.uri_path
    
    @property
    def change_count(self):
        """The number of known change events"""
        return len(self.changes)
        
    def generate(self, from_changeid=None):
        """Generates an inventory of changes"""
        if from_changeid==None:
            from_changeid=self.first_change_id
        from_changeid = int(from_changeid)
        changeset = ChangeSet()
        for change in self.changes_from(from_changeid):
            changeset.add(change)
        changeset.capabilities[self.next_changeset_uri()] = {
                                                "rel": "next rs:changeset"}
        changeset.capabilities[self.current_changeset_uri(from_changeid)] = {
                                                "rel": "current rs:changeset"}
        return changeset
    
    def notify(self, change):
        """Simply store a change in the in-memory list"""
        self.logger.info(str(change))
        change.changeid = self.latest_change_id + 1
        self.latest_change_id = change.changeid
        if self.max_changes != -1 and self.change_count >= self.max_changes:
            del self.changes[0]
            self.first_change_id = self.changes[0].changeid
        self.changes.append(change)
    
    def current_changeset_uri(self, from_changeid = None):
        """Constructs the URI of the current changeset."""
        if from_changeid is None:
            return self.base_uri + "/from/" + str(self.first_change_id)
        else:
            return self.base_uri + "/from/" + str(from_changeid)
    
    def next_changeset_uri(self):
        """Constructs the URI of the next changeset"""
        return self.base_uri + "/from/" + str(self.latest_change_id + 1)
    
    def changes_from(self, changeid):
        """Returns all changes starting from (and including) a certain
        changeid"""
        changeid = int(changeid)
        changes = [change for change in self.changes 
                            if change.changeid >= changeid]
        return sorted(changes, key=lambda change: change.changeid)
    
    def knows_changeid(self, changeid = None):
        """Returns true if changeid is known (= stored)"""
        changeid = int(changeid)
        known = ((self.first_change_id <= changeid)
                    and (changeid <= self.latest_change_id))
        return known
