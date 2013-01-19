#!/usr/bin/env python
# encoding: utf-8
"""
source.py: A source holds a set of resources and changes over time.

Resources are internally stored by their basename (e.g., 1) for memory
efficiency reasons.

Created by Bernhard Haslhofer on 2012-04-24.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

import re
import os
import random
import pprint
import logging
import time
import shutil

from apscheduler.scheduler import Scheduler

from simulator.observer import Observable
from resync.resource import Resource
from resync.utils import compute_md5_for_string
from resync.resourcelist import ResourceList
from resync.sitemap import Sitemap, Mapper

#### Source-specific capability implementations ####

class DynamicResourceListBuilder(object):
    """Generates an resourcelist snapshot from a source"""
    
    def __init__(self, source, config):
        self.source = source
        self.config = config
        self.logger = logging.getLogger('resourcelist_builder')
        
    def bootstrap(self):
        """Bootstrapping procedures implemented in subclasses"""
        pass
    
    @property
    def path(self):
        """The resourcelist path (from the config file)"""
        return self.config['uri_path']

    @property
    def uri(self):
        """The resourcelist URI (e.g., http://localhost:8080/resourcelist.xml)"""
        return self.source.base_uri + "/" + self.path
    
    def generate(self):
        """Generates an resourcelist (snapshot from the source)"""
        then = time.time()
        capabilities = {}
        if self.source.has_changememory:
            next_changelist = self.source.changememory.next_changelist_uri()
            capabilities[next_changelist] = {"type": "changelist"}
        resourcelist = ResourceList(resources=self.source.resources,
                              capabilities=capabilities)
        now = time.time()
        self.logger.info("Generated resourcelist: %f" % (now-then))
        return resourcelist
        
class StaticResourceListBuilder(DynamicResourceListBuilder):
    """Periodically writes an resourcelist to the file system"""
    
    def __init__(self, source, config):
        super(StaticResourceListBuilder, self).__init__(source, config)
                                
    def bootstrap(self):
        """Bootstraps the static resourcelist writer background job"""
        self.rm_sitemap_files(Source.STATIC_FILE_PATH)
        self.write_static_resourcelist()
        logging.basicConfig()
        interval = self.config['interval']
        sched = Scheduler()
        sched.start()
        sched.add_interval_job(self.write_static_resourcelist,
                                seconds=interval)
        
    def write_static_resourcelist(self):
        """Writes the resourcelist to the filesystem"""
        # Generate sitemap in temp directory
        then = time.time()
        self.ensure_temp_dir(Source.TEMP_FILE_PATH)
        resourcelist = self.generate()
        basename = Source.TEMP_FILE_PATH + "/resourcelist.xml"
        s=Sitemap()
        s.max_sitemap_entries=self.config['max_sitemap_entries']
        s.mapper=Mapper([self.source.base_uri, Source.TEMP_FILE_PATH])
        s.write(resourcelist, basename)
        # Delete old sitemap files; move the new ones; delete the temp dir
        self.rm_sitemap_files(Source.STATIC_FILE_PATH)
        self.mv_sitemap_files(Source.TEMP_FILE_PATH, Source.STATIC_FILE_PATH)
        shutil.rmtree(Source.TEMP_FILE_PATH)
        now = time.time()
        # Log Sitemap create start event
        sitemap_size = self.compute_sitemap_size(Source.STATIC_FILE_PATH)
        log_data = {'time': (now-then), 
                    'no_resources': self.source.resource_count}
        self.logger.info("Wrote static sitemap resourcelist. %s" % log_data)
        sm_write_end = Resource(
                resource = Resource(self.uri, 
                                size=sitemap_size,
                                timestamp=then),
                                change = "updated")
        self.source.notify_observers(sm_write_end)
        
    def ensure_temp_dir(self, temp_dir):
        """Create temp directory if it doesn't exist; removes existing one"""
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)
        else:
            os.makedirs(temp_dir)
    
    def ls_sitemap_files(self, directory):
        """Returns the list of sitemaps in a directory"""
        p = re.compile('sitemap\d*\.xml')
        filelist = [ f for f in os.listdir(directory) if p.match(f) ]
        return filelist
    
    def rm_sitemap_files(self, directory):
        """Deletes sitemap files (from previous runs)"""
        filelist = self.ls_sitemap_files(directory)
        if len(filelist) > 0:
            self.logger.debug("*** Cleaning up %d sitemap files ***" % 
                                                                len(filelist))
            for f in filelist:
                filepath = directory + "/" + f
                os.remove(filepath)
    
    def mv_sitemap_files(self, src_directory, dst_directory):
        """Moves sitemaps from src to dst directory"""
        filelist = self.ls_sitemap_files(src_directory)
        if len(filelist) > 0:
            self.logger.debug("*** Moving %d sitemap files ***" % 
                                                                len(filelist))
            for f in filelist:
                filepath = src_directory + "/" + f
                shutil.move(filepath, dst_directory)
    
    def compute_sitemap_size(self, directory):
        """Computes the size of all sitemap files in a given directory"""
        return sum([os.stat(directory + "/" + f).st_size 
                        for f in self.ls_sitemap_files(directory)])
    
#### Source Simulator ####

class Source(Observable):
    """A source contains a list of resources and changes over time"""
    
    RESOURCE_PATH = "/resources"
    STATIC_FILE_PATH = os.path.join(os.path.dirname(__file__), "static")
    TEMP_FILE_PATH = os.path.join(os.path.dirname(__file__), "temp")
    
    def __init__(self, config, hostname, port):
        """Initalize the source"""
        super(Source, self).__init__()
        self.logger = logging.getLogger('source')
        self.config = config
        self.logger.info("Source config: %s " % self.config)
        self.hostname = hostname
        self.port = port
        self.max_res_id = 1
        self._repository = {} # {basename, {timestamp, size}}
        self.resourcelist_builder = None # The resourcelist builder implementation
        self.changememory = None # The change memory implementation
        self.no_events = 0
    
    ##### Source capabilities #####
    
    def add_resourcelist_builder(self, resourcelist_builder):
        """Adds an resourcelist builder implementation"""
        self.resourcelist_builder = resourcelist_builder
        
    @property
    def has_resourcelist_builder(self):
        """Returns True in the Source has an resourcelist builder"""
        return bool(self.resourcelist_builder is not None)        
    
    def add_changememory(self, changememory):
        """Adds a changememory implementation"""
        self.changememory = changememory
        
    @property
    def has_changememory(self):
        """Returns True if a source maintains a change memory"""
        return bool(self.changememory is not None)
    
    ##### Bootstrap Source ######

    def bootstrap(self):
        """Bootstrap the source with a set of resources"""
        self.logger.info("Bootstrapping source...")
        for i in range(self.config['number_of_resources']):
            self._create_resource(notify_observers = False)
        if self.has_changememory: self.changememory.bootstrap()
        if self.has_resourcelist_builder: self.resourcelist_builder.bootstrap()
        self._log_stats()
    
    ##### Source data accessors #####
    
    @property
    def base_uri(self):
        """Returns the base URI of the source (e.g., http://localhost:8888)"""
        return "http://" + self.hostname + ":" + str(self.port)

    @property
    def resource_count(self):
        """The number of resources in the source's repository"""
        return len(self._repository)
    
    @property
    def resources(self):
        """Iterates over resources and yields resource objects"""
        repository = self._repository
        for basename in repository.keys():
            resource = self.resource(basename)
            if resource is None:
                self.logger.error("Cannot create resource %s " % basename + \
                      "because source object has been deleted.")
            yield resource
    
    @property
    def random_resource(self):
        """Returns a single random resource"""
        rand_res = self.random_resources()
        if len(rand_res) == 1:
            return rand_res[0]
        else:
            return None
    
    def resource(self, basename):
        """Creates and returns a resource object from internal resource
        repository. Repositoy values are copied into the object."""
        if not self._repository.has_key(basename): return None
        uri = self.base_uri + Source.RESOURCE_PATH + "/" + basename
        timestamp = self._repository[basename]['timestamp']
        size = self._repository[basename]['size']
        md5 = compute_md5_for_string(self.resource_payload(basename, size))
        return Resource(uri = uri, timestamp = timestamp, size = size,
                        md5 = md5)
    
    def resource_payload(self, basename, size = None):
        """Generates dummy payload by repeating res_id x size times"""
        if size == None: size = self._repository[basename]['size']
        no_repetitions = size / len(basename)
        content = "".join([basename for x in range(no_repetitions)])
        no_fill_chars = size % len(basename)
        fillchars = "".join(["x" for x in range(no_fill_chars)])
        return content + fillchars
    
    def random_resources(self, number = 1):
        "Return a random set of resources, at most all resources"
        if number > len(self._repository):
            number = len(self._repository)
        rand_basenames = random.sample(self._repository.keys(), number)
        return [self.resource(basename) for basename in rand_basenames]
    
    def simulate_changes(self):
        """Simulate changing resources in the source"""
        self.logger.info("Starting simulation...")
        sleep_time = self.config['change_delay']
        while self.no_events != self.config['max_events']:
            time.sleep(sleep_time)
            event_type = random.choice(self.config['event_types'])
            if event_type == "create":
                self._create_resource()
            elif event_type == "update" or event_type == "delete":
                if len(self._repository.keys()) > 0:
                    basename = random.sample(self._repository.keys(), 1)[0]
                else:
                    basename = None
                if basename is None: 
                    self.no_events = self.no_events + 1                    
                    continue
                if event_type == "update":
                    self._update_resource(basename)
                elif event_type == "delete":
                    self._delete_resource(basename)

            else:
                self.logger.error("Event type %s is not supported" 
                                                                % event_type)
            self.no_events = self.no_events + 1
            if self.no_events%self.config['stats_interval'] == 0:
                self._log_stats()

        self.logger.info("Finished change simulation")
    
    # Private Methods
    
    def _create_resource(self, basename = None, notify_observers = True):
        """Create a new resource, add it to the source, notify observers."""
        if basename == None:
            basename = str(self.max_res_id)
            self.max_res_id += 1
        timestamp = time.time()
        size = random.randint(0, self.config['average_payload'])
        self._repository[basename] = {'timestamp': timestamp, 'size': size}
        if notify_observers:
            change = Resource(
                        resource = self.resource(basename),
                        change = "created")
            self.notify_observers(change)
        
    def _update_resource(self, basename):
        """Update a resource, notify observers."""
        self._delete_resource(basename, notify_observers = False)
        self._create_resource(basename, notify_observers = False)
        change = Resource(
                    resource = self.resource(basename),
                    change = "updated")
        self.notify_observers(change)

    def _delete_resource(self, basename, notify_observers = True):
        """Delete a given resource, notify observers."""
        res = self.resource(basename)
        del self._repository[basename]
        res.timestamp = time.time()
        if notify_observers:
            change = Resource(
                        resource = res,
                        change = "deleted")
            self.notify_observers(change)
    
    def _log_stats(self):
        """Output current source statistics via the logger"""
        stats = {
            'no_resources': self.resource_count,
            'no_events': self.no_events
        }
        self.logger.info("Source stats: %s" % stats)
    
    def __str__(self):
        """Prints out the source's resources"""
        return pprint.pformat(self._repository)
