#!/usr/bin/env python
# encoding: utf-8
"""
source.py: A source holds a set of resources and changes over time.

Resources are internally stored by their basename (e.g., 1) for memory
efficiency reasons.

Created by Bernhard Haslhofer on 2012-04-24.
"""

import os
import random
import pprint
import logging
import time

from resync.utils import compute_md5_for_string
from resync.resource_list import ResourceList

from simulator.observer import Observable
from simulator.resource import Resource


# Source-specific capability implementations

class DynamicResourceListBuilder(object):
    """Generates an resource_list snapshot from a source."""

    def __init__(self, source, config):
        """Initialize the DynamicResourceListBuilder."""
        self.source = source
        self.config = config
        self.logger = logging.getLogger('resource_list_builder')

    def bootstrap(self):
        """Bootstrapping procedures implemented in subclasses."""
        pass

    @property
    def path(self):
        """The resource_list path from the config file."""
        return self.config['uri_path']

    @property
    def uri(self):
        """The resource_list URI.

        e.g., http://localhost:8080/resourcelist.xml
        """
        return self.source.base_uri + "/" + self.path

    def generate(self):
        """Generate a resource_list (snapshot from the source)."""
        then = time.time()
        resource_list = ResourceList(
            resources=self.source.resources, count=self.source.resource_count)
        now = time.time()
        self.logger.info("Generated resource_list: %f" % (now - then))
        return resource_list


class Source(Observable):
    """A source contains a list of resources and changes over time."""

    RESOURCE_PATH = "/resources"  # to append to base_uri
    STATIC_FILE_PATH = os.path.join(os.path.dirname(__file__), "static")

    def __init__(self, config, base_uri, port):
        """Initalize the source."""
        super(Source, self).__init__()
        self.logger = logging.getLogger('source')
        self.config = config
        self.logger.info("Source config: %s " % self.config)
        self.port = port
        self.base_uri = base_uri
        self.max_res_id = 1
        self._repository = {}  # {basename, {timestamp, length}}
        self.resource_list_builder = None  # builder implementation
        self.changememory = None  # change memory implementation
        self.no_events = 0

    # Source capabilities

    def add_resource_list_builder(self, resource_list_builder):
        """Add a resource_list builder implementation."""
        self.resource_list_builder = resource_list_builder

    @property
    def has_resource_list_builder(self):
        """Return True if the Source has an resource_list builder."""
        return bool(self.resource_list_builder is not None)

    def add_changememory(self, changememory):
        """Add a changememory implementation."""
        self.changememory = changememory

    @property
    def has_changememory(self):
        """Return True if a source maintains a change memory."""
        return bool(self.changememory is not None)

    # Bootstrap Source

    def bootstrap(self):
        """Bootstrap the source with a set of resources."""
        self.logger.info("Bootstrapping source...")
        for i in range(self.config['number_of_resources']):
            self._create_resource(notify_observers=False)
        if self.has_changememory:
            self.changememory.bootstrap()
        if self.has_resource_list_builder:
            self.resource_list_builder.bootstrap()
        self._log_stats()

    # Source data accessors

    @property
    def describedby_uri(self):
        """Description of Source, here assume base_uri."""
        return self.base_uri

    @property
    def source_description_uri(self):
        """URI of Source Description document.

        Will use standard pattern for well-known URI unless
        an explicit configuration is given.
        """
        if ('source_description_uri' in self.config):
            return self.config['source_description_uri']
        return self.base_uri + '/.well-known/resourcesync'

    @property
    def capability_list_uri(self):
        """URI of Capability List Document."""
        return self.base_uri + '/capabilitylist.xml'

    @property
    def resource_count(self):
        """The number of resources in the source's repository."""
        return len(self._repository)

    @property
    def resources(self):
        """Iterate over resources and yields resource objects."""
        repository = self._repository
        for basename in repository.keys():
            resource = self.resource(basename)
            if resource is None:
                self.logger.error("Cannot create resource %s " % basename +
                                  "because source object has been deleted.")
            yield resource

    @property
    def random_resource(self):
        """Return a single random resource."""
        rand_res = self.random_resources()
        if len(rand_res) == 1:
            return rand_res[0]
        else:
            return None

    def resource(self, basename):
        """Create and return a resource object.

        Details of the resource with basename are taken from the
        internal resource repository. Repositoy values are copied
        into the object.
        """
        if basename not in self._repository:
            return None
        uri = self.base_uri + Source.RESOURCE_PATH + "/" + basename
        timestamp = self._repository[basename]['timestamp']
        length = self._repository[basename]['length']
        md5 = compute_md5_for_string(self.resource_payload(basename, length))
        return Resource(uri=uri, timestamp=timestamp, length=length,
                        md5=md5)

    def resource_payload(self, basename, length=None):
        """Generate dummy payload by repeating res_id x length times."""
        if length is None:
            length = self._repository[basename]['length']
        no_repetitions = length // len(basename)
        content = "".join([basename for x in range(no_repetitions)])
        no_fill_chars = length % len(basename)
        fillchars = "".join(["x" for x in range(no_fill_chars)])
        return content + fillchars

    def random_resources(self, number=1):
        """Return a random set of resources, at most all resources."""
        if number > len(self._repository):
            number = len(self._repository)
        rand_basenames = random.sample(self._repository.keys(), number)
        return [self.resource(basename) for basename in rand_basenames]

    def simulate_changes(self):
        """Simulate changing resources in the source."""
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
            if self.no_events % self.config['stats_interval'] == 0:
                self._log_stats()

        self.logger.info("Finished change simulation")

    # Private Methods

    def _create_resource(self, basename=None, notify_observers=True):
        """Create a new resource, add it to the source, notify observers."""
        if basename is None:
            basename = str(self.max_res_id)
            self.max_res_id += 1
        timestamp = time.time()
        length = random.randint(0, self.config['average_payload'])
        self._repository[basename] = {'timestamp': timestamp, 'length': length}
        if notify_observers:
            change = Resource(
                resource=self.resource(basename), change="created")
            self.notify_observers(change)

    def _update_resource(self, basename):
        """Update a resource, notify observers."""
        self._delete_resource(basename, notify_observers=False)
        self._create_resource(basename, notify_observers=False)
        change = Resource(
            resource=self.resource(basename), change="updated")
        self.notify_observers(change)

    def _delete_resource(self, basename, notify_observers=True):
        """Delete a given resource, notify observers."""
        res = self.resource(basename)
        del self._repository[basename]
        res.timestamp = time.time()
        if notify_observers:
            change = Resource(
                uri=res.uri, timestamp=res.timestamp, change="deleted")
            self.notify_observers(change)

    def _log_stats(self):
        """Output current source statistics via the logger."""
        stats = {
            'no_resources': self.resource_count,
            'no_events': self.no_events
        }
        self.logger.info("Source stats: %s" % stats)

    def __str__(self):
        """Print out the source's resources."""
        return pprint.pformat(self._repository)
