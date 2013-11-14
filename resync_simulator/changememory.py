#!/usr/bin/env python
# encoding: utf-8
"""
changememory.py: A record of change events

Created by Bernhard Haslhofer on 2012-04-27.

"""
import logging

from resync.change_list import ChangeList

from resync_simulator.observer import Observer


class ChangeMemory(Observer):
    """An abstract change memory implementation that doesn't do anything.
    ChangeMemory implementations can extend this class

    If max_changes is True then the number of changes stored will be limited
    to the number specified.
    """

    def __init__(self, source, config):
        self.source = source
        self.config = config
        self.uri_path = config['uri_path']
        self.max_changes = config['max_changes']
        self.changes = []  # stores change events; sorted by event id
        source.register_observer(self)
        self.logger = logging.getLogger('changememory')
        self.logger.info("Changememory config: %s " % self.config)

    def bootstrap(self):
        """Bootstrap the Changememory; should be overridden by subclasses"""
        pass

    @property
    def change_count(self):
        """The number of cached known change events"""
        return len(self.changes)

    def notify(self, change):
        """General procdures for incoming changes. Should be overridden."""
        self.logger.info("Event: %s" % str(change))


# A dynamic in-memory change set
class DynamicChangeList(ChangeMemory):
    """A change memory that stores changes in an in-memory list"""

    def __init__(self, source, config):
        super(DynamicChangeList, self).__init__(source, config)
        self.last_index=-1

    @property
    def base_uri(self):
        """Returns the changememory's URI"""
        return self.source.base_uri + "/" + self.uri_path

    def generate(self):
        """Generates a list of changes"""
        changelist = ChangeList()
        for change in self.changes:
            changelist.add(change)
        return changelist

    def generate_incremental(self):
        """Generates a list of changes"""
        #FIXME - not safe for multiple clients!
        changelist = ChangeList()
        first = 0 if (self.last_index<=0) else (self.last_index+1)
        for change in self.changes[first:]:
            changelist.add(change)
        self.last_index=len(self.changes)-1
        return changelist

    def notify(self, change):
        """Simply store a change in the in-memory list"""
        super(DynamicChangeList, self).notify(change)
        self.changes.append(change)
        if (self.max_changes and 
            len(self.changes)>self.max_changes):
            num_to_delete = (len(self.changes)-self.max_changes)
            self.last_index -= num_to_delete
            del self.changes[0:num_to_delete]
