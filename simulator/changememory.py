#!/usr/bin/env python
# encoding: utf-8
"""
changememory.py: A record of change events

Created by Bernhard Haslhofer on 2012-04-27.
Copyright 2012, ResourceSync.org. All rights reserved.
"""
import logging
import re
import os
import time

from resync.changelist import ChangeList
from resync.sitemap import Sitemap, Mapper

from simulator.observer import Observer
from simulator.source import Source

class ChangeMemory(Observer):
    """An abstract change memory implementation that doesn't do anything.
    ChangeMemory implementations can extend this class
    """
    
    def __init__(self, source, config):
        self.source = source
        self.config = config
        self.uri_path = config['uri_path']
        self.max_changes = config['max_changes']
        self.changes = [] # stores change events; sorted by event id
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
        self.logger.info("Event: %s" % repr(change))

# A dynamic in-memory change set
class DynamicChangeList(ChangeMemory):
    """A change memory that stores changes in an in-memory list"""

    def __init__(self, source, config):
        super(DynamicChangeList, self).__init__(source, config)
        self.latest_change_id = 0
        self.first_change_id = 0
                
    @property
    def base_uri(self):
        """Returns the changememory's URI"""
        return self.source.base_uri + "/" + self.uri_path
    
    def generate(self, from_changeid=None):
        """Generates a list of changes"""
        if from_changeid==None:
            from_changeid=self.first_change_id
        from_changeid = int(from_changeid)
        changelist = ChangeList()
        for change in self.changes_from(from_changeid):
            changelist.add(change)
        changelist.capabilities[self.next_changelist_uri()] = {
                "rel": "next http://www.openarchives.org/rs/changelist"}
        changelist.capabilities[self.current_changelist_uri(from_changeid)] = {
                "rel": "current http://www.openarchives.org/rs/changelist"}
        return changelist
    
    def notify(self, change):
        """Simply store a change in the in-memory list"""
        super(DynamicChangeList, self).notify(change)
        change.changeid = self.latest_change_id + 1
        self.latest_change_id = change.changeid
        if self.max_changes != -1 and self.change_count >= self.max_changes:
            del self.changes[0]
            self.first_change_id = self.changes[0].changeid
        self.changes.append(change)
    
    def current_changelist_uri(self, from_changeid = None):
        """Constructs the URI of the current changelist."""
        if from_changeid is None:
            return self.base_uri + "/from/" + str(self.first_change_id)
        else:
            return self.base_uri + "/from/" + str(from_changeid)
    
    def next_changelist_uri(self):
        """Constructs the URI of the next changelist"""
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

# A static file-based change memory
class StaticChangeList(ChangeMemory):
    """A changememory that periodically dumps changes to the file system"""
    
    def __init__(self, source, config):
        super(StaticChangeList, self).__init__(source, config)
        self.uri_file = config['uri_file']
        self.previous_changelist_id = 0
    
    @property
    def base_uri(self):
        """Returns the changememory's URI"""
        return self.source.base_uri + "/" + self.uri_path + "/" + self.uri_file
    
    def bootstrap(self):
        """Procedures to be performed at startup-time"""
        self.rm_changelist_files(Source.STATIC_FILE_PATH)
    
    def next_changelist_uri(self):
        """Constructs the URI of the next changelist"""
        return self.base_uri

    def current_changelist_uri(self):
        """Constructs the URI of the next changelist"""
        return self.base_uri
    
    def previous_changelist_uri(self):
        """Constructs the URI of the previous changelist; None if there is no
        previous changelist"""
        if self.previous_changelist_id == 0:
            return None
        else:
            path = self.source.base_uri + "/" + self.uri_path
            return path + "/" + self.previous_changelist_file()
    
    def previous_changelist_file(self):
        """Constructus the previous changelist's filename"""
        return "changelist%05d.xml" % self.previous_changelist_id
    
    def current_changelist_file(self):
        """Constructs the filename the current changes to be written"""
        return "changelist%05d.xml" % (self.previous_changelist_id + 1)
    
    def generate(self):
        """Generates a list of changes"""
        changelist = ChangeList()
        for change in self.changes:
            changelist.add(change)
        changelist.capabilities[self.current_changelist_uri()] = {
                "rel": "current http://www.openarchives.org/rs/changelist"}
        if self.previous_changelist_uri() is not None:
            changelist.capabilities[self.previous_changelist_uri()] = {
                "rel": "previous http://www.openarchives.org/rs/changelist"}
        return changelist
    
    def notify(self, change):
        """Simply store a change in the in-memory list"""
        super(StaticChangeList, self).notify(change)
        self.changes.append(change)
        if len(self.changes) >= self.config['max_changes']:
            self.write_changelist()
            del self.changes[:]
    
    def write_changelist(self):
        """Writes all cached changes to a file; empties the cache"""
        then = time.time()
        changelist = self.generate()
        basename = Source.STATIC_FILE_PATH + "/" + self.current_changelist_file()
        s=Sitemap()
        s.max_sitemap_entries=self.config['max_sitemap_entries']
        s.mapper=Mapper([self.source.base_uri, Source.STATIC_FILE_PATH])
        s.write(changelist, basename)
        now = time.time()
        # sitemap_size = 50
        log_data = {}
        # log_data = {'time': (now-then), 
        #             'no_resources': self.source.resource_count}
        self.previous_changelist_id = self.previous_changelist_id + 1
        self.logger.info("Wrote static changelist. %s" % log_data)
    
    def ls_changelist_files(self, directory):
        """Returns the list of changelists in a directory"""
        p = re.compile('changelist\d*\.xml')
        filelist = [ f for f in os.listdir(directory) if p.match(f) ]
        return filelist

    def rm_changelist_files(self, directory):
        """Deletes changeest files (from previous runs)"""
        filelist = self.ls_changelist_files(directory)
        if len(filelist) > 0:
            self.logger.debug("Cleaning up %d changelist files" % 
                                                                len(filelist))
            for f in filelist:
                filepath = directory + "/" + f
                os.remove(filepath)
