#!/usr/bin/env python
# encoding: utf-8
"""
changememory.py: A record of change events.

Created by Bernhard Haslhofer on 2012-04-27.

"""
import logging

from resync.change_list import ChangeList

from simulator.observer import Observer


class ChangeMemory(Observer):
    """An abstract change memory implementation.

    This class doesn't do anything, ChangeMemory implementations
    should extend this class.

    If max_changes is True then the number of changes stored will be limited
    to the number specified.
    """

    def __init__(self, source, config):
        """Initialize ChangeMemory with source and config."""
        self.source = source
        self.config = config
        self.uri_path = config['uri_path']
        self.max_changes = config['max_changes']
        self.changes = []  # stores change events; sorted by event id
        source.register_observer(self)
        self.logger = logging.getLogger('changememory')
        self.logger.info("Changememory config: %s " % self.config)

    def bootstrap(self):
        """Bootstrap the Changememory; should be overridden by subclasses."""
        pass

    @property
    def change_count(self):
        """The number of cached known change events."""
        return len(self.changes)

    def notify(self, change):
        """General procdures for incoming changes. Should be overridden."""
        self.logger.info("Event: %s" % repr(change))


# A dynamic in-memory change set
class DynamicChangeList(ChangeMemory):
    """A change memory that stores changes in an in-memory list."""

    def __init__(self, source, config):
        """Initialize DynamicChangeList with source and config."""
        super(DynamicChangeList, self).__init__(source, config)

    @property
    def base_uri(self):
        """Return the changememory's URI."""
        return self.source.base_uri + "/" + self.uri_path

    def generate(self):
        """Generate a list of changes."""
        changelist = ChangeList()
        for change in self.changes:
            changelist.add(change)
        return changelist

    def notify(self, change):
        """Simply store a change in the in-memory list."""
        super(DynamicChangeList, self).notify(change)
        self.changes.append(change)
        if (self.max_changes and
                len(self.changes) > self.max_changes):
            del self.changes[0:(len(self.changes) - self.max_changes)]
