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

from resync.observer import Observer
from resync.changeset import ChangeSet
from resync.source import Source
from resync.sitemap import Sitemap, Mapper

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
        pass

# A dynamic in-memory change set
class DynamicChangeSet(ChangeMemory):
    """A change memory that stores changes in an in-memory list"""

    def __init__(self, source, config):
        super(DynamicChangeSet, self).__init__(source, config)
        self.latest_change_id = 0
        self.first_change_id = 0
                
    @property
    def base_uri(self):
        """Returns the changememory's URI"""
        return self.source.base_uri + "/" + self.uri_path
    
    def generate(self, from_changeid=None):
        """Generates an inventory of changes"""
        if from_changeid==None:
            from_changeid=self.first_change_id
        from_changeid = int(from_changeid)
        changeset = ChangeSet()
        for change in self.changes_from(from_changeid):
            changeset.add(change)
        changeset.capabilities[self.next_changeset_uri()] = {
                "rel": "next http://www.openarchives.org/rs/changeset"}
        changeset.capabilities[self.current_changeset_uri(from_changeid)] = {
                "rel": "current http://www.openarchives.org/rs/changeset"}
        return changeset
    
    def notify(self, change):
        """Simply store a change in the in-memory list"""
        super(DynamicChangeSet, self).notify(change)
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

# A static file-based change memory
class StaticChangeSet(ChangeMemory):
    """A changememory that periodically dumps changes to the file system"""
    
    def __init__(self, source, config):
        super(StaticChangeSet, self).__init__(source, config)
        self.uri_file = config['uri_file']
        self.previous_changeset_id = 0
    
    @property
    def base_uri(self):
        """Returns the changememory's URI"""
        return self.source.base_uri + "/" + self.uri_path + "/" + self.uri_file
    
    def bootstrap(self):
        """Procedures to be performed at startup-time"""
        self.rm_changeset_files(Source.STATIC_FILE_PATH)
    
    def next_changeset_uri(self):
        """Constructs the URI of the next changeset"""
        return self.base_uri

    def current_changeset_uri(self):
        """Constructs the URI of the next changeset"""
        return self.base_uri
    
    def previous_changeset_uri(self):
        """Constructs the URI of the previous changeset; None if there is no
        previous changeset"""
        if self.previous_changeset_id == 0:
            return None
        else:
            path = self.source.base_uri + "/" + self.uri_path
            return path + "/" + self.previous_changeset_file()
    
    def previous_changeset_file(self):
        """Constructus the previous changeset's filename"""
        return "changeset%05d.xml" % self.previous_changeset_id
    
    def current_changeset_file(self):
        """Constructs the filename the current changes to be written"""
        return "changeset%05d.xml" % (self.previous_changeset_id + 1)
    
    def generate(self):
        """Generates an inventory of changes"""
        changeset = ChangeSet()
        for change in self.changes:
            changeset.add(change)
        changeset.capabilities[self.current_changeset_uri()] = {
                "rel": "current http://www.openarchives.org/rs/changeset"}
        if self.previous_changeset_uri() is not None:
            changeset.capabilities[self.previous_changeset_uri()] = {
                "rel": "previous http://www.openarchives.org/rs/changeset"}
        return changeset
    
    def notify(self, change):
        """Simply store a change in the in-memory list"""
        super(StaticChangeSet, self).notify(change)
        self.changes.append(change)
        if len(self.changes) >= self.config['max_changes']:
            self.write_changeset()
            del self.changes[:]
    
    def write_changeset(self):
        """Writes all cached changes to a file; empties the cache"""
        then = time.time()
        changeset = self.generate()
        basename = Source.STATIC_FILE_PATH + "/" + self.current_changeset_file()
        s=Sitemap()
        s.max_sitemap_entries=self.config['max_sitemap_entries']
        s.mapper=Mapper([self.source.base_uri, Source.STATIC_FILE_PATH])
        s.write(changeset, basename)
        now = time.time()
        self.previous_changeset_id = self.previous_changeset_id + 1
        self.logger.info("Wrote static changeset..")
    
    def ls_changeset_files(self, directory):
        """Returns the list of changesets in a directory"""
        p = re.compile('changeset\d*\.xml')
        filelist = [ f for f in os.listdir(directory) if p.match(f) ]
        return filelist

    def rm_changeset_files(self, directory):
        """Deletes changeest files (from previous runs)"""
        filelist = self.ls_changeset_files(directory)
        if len(filelist) > 0:
            self.logger.info("Cleaning up %d changeset files" % 
                                                                len(filelist))
            for f in filelist:
                filepath = directory + "/" + f
                os.remove(filepath)