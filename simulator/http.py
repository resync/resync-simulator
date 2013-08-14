#!/usr/bin/env python
# encoding: utf-8
"""
http.py: The source's HTTP Web interface running on the
non-blocking Tornado web server (http://www.tornadoweb.org/)

Created by Bernhard Haslhofer on 2012-04-24.
"""

import threading
import os.path
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.web

from resync.source_description import SourceDescription
from resync.capability_list import CapabilityList
from resync.change_list import ChangeList

from simulator.source import Source


class HTTPInterface(threading.Thread):
    """The repository's HTTP interface. To make sure it doesn't interrupt
    the simulation, it runs in a separate thread.

    http://stackoverflow.com/questions/323972/
        is-there-any-way-to-kill-a-thread-in-python (Stoppable Threads)

    http://www.slideshare.net/juokaz/
        restful-web-services-with-python-dynamic-languages-conference

    """

    def __init__(self, source):
        """Initializes HTTP interface with default settings and handlers"""
        super(HTTPInterface, self).__init__()
        self.logger = logging.getLogger('http')
        self._stop = threading.Event()
        self.source = source
        self.port = source.port
        self.settings = dict(
            title=u"ResourceSync Change Simulator",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=Source.STATIC_FILE_PATH,
            autoescape=None,
        )
        self.handlers = [
            (r"/", HomeHandler, dict(source=self.source)),
            (r"/\.well-known/resourcesync", SourceDescriptionHandler,
                dict(source=self.source)),
            (r"/capabilitylist\.xml", CapabilityListHandler,
                dict(source=self.source)),
            (r"%s" % Source.RESOURCE_PATH, ResourcesHandler,
                dict(source=self.source)),
            (r"%s/([0-9]+)" % Source.RESOURCE_PATH, ResourceHandler,
                dict(source=self.source)),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
                dict(path=self.settings['static_path'])),
        ]

        """Initialize resource_list handlers"""
        if self.source.has_resource_list_builder:
            resource_list_builder = self.source.resource_list_builder
            if resource_list_builder.config['class'] == "DynamicResourceListBuilder":
                self.handlers = self.handlers + \
                    [(r"/%s" % resource_list_builder.path,
                        ResourceListHandler,
                        dict(resource_list_builder=resource_list_builder,
                             source=self.source))]

        """Initialize changememory handlers"""
        if self.source.has_changememory:
            changememory = self.source.changememory
            if changememory.config['class'] == "DynamicChangeList":
                self.handlers = self.handlers + \
                    [(r"/%s" % changememory.uri_path,
                        DynamicChangeListHandler,
                        dict(changememory=changememory,
                             source=self.source))]

    def run(self):
        self.logger.info("Starting up HTTP Interface on port %i" % (self.port))
        application = tornado.web.Application(
            handlers=self.handlers,
            debug=True,
            **self.settings)
        self.http_server = tornado.httpserver.HTTPServer(application)
        self.http_server.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        self.logger.info("Stopping HTTP Interface")
        tornado.ioloop.IOLoop.instance().stop()
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


class BaseRequestHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ("GET")

    def initialize(self, source):
        self.source = source


class HomeHandler(BaseRequestHandler):
    """Root URI handler"""
    def get(self):
        self.render("home.html",
                    resource_count=self.source.resource_count,
                    source=self.source)

# Resource Handlers


class ResourcesHandler(BaseRequestHandler):
    """Resources subset selection handler"""
    def get(self):
        rand_res = sorted(self.source.random_resources(100),
                          key=lambda res: int(res.basename))
        self.render("resource.index.html",
                    resources=rand_res,
                    source=self.source)

# Source Description Handler


class SourceDescriptionHandler(BaseRequestHandler):
    """The HTTP request handler for the Source Description"""
    def get(self):
        source_description = SourceDescription()
        source_description.describedby = self.source.describedby_uri
        source_description.add_capability_list(self.source.capability_list_uri)
        self.set_header("Content-Type", "application/xml")
        self.write(source_description.as_xml())


# Capability List Handler


class CapabilityListHandler(BaseRequestHandler):
    """The HTTP request handler for the Capability List"""
    def get(self):
        capability_list = CapabilityList()
        capability_list.describedby = self.source.describedby_uri
        capability_list.add_capability(uri=self.source.resource_list_builder.uri,
                                       name='resourcelist')
        if self.source.has_changememory:
            capability_list.add_capability(uri=self.source.changememory.base_uri,
                                           name='changelist')
        self.set_header("Content-Type", "application/xml")
        self.write(capability_list.as_xml())

# Resource Handler


class ResourceHandler(BaseRequestHandler):
    """Resource handler"""
    def get(self, basename):
        resource = self.source.resource(basename)
        if resource is None:
            self.send_error(404)
        else:
            self.set_header("Content-Type", "text/plain")
            self.set_header("Content-Length", resource.length)
            self.set_header("Last-Modified", resource.lastmod)
            self.set_header("Etag", "\"%s\"" % resource.md5)
            payload = self.source.resource_payload(basename)
            self.write(payload)

# ResourceList Handlers


class ResourceListHandler(tornado.web.RequestHandler):
    """The HTTP request handler for the ResourceList"""

    def initialize(self, source, resource_list_builder):
        self.source = source
        self.resource_list_builder = resource_list_builder

    def generate_resource_list(self):
        """Creates a resource_list"""
        resource_list = self.resource_list_builder.generate()
        resource_list.describedby = self.source.describedby_uri
        resource_list.up = self.source.capability_list_uri
        resource_list.md_at = 'now'
        return resource_list.as_xml()

    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.write(self.generate_resource_list())

# Changememory Handlers


class DynamicChangeListHandler(tornado.web.RequestHandler):
    """The HTTP request handler for dynamically generated changelists"""

    def initialize(self, source, changememory):
        self.source = source
        self.changememory = changememory

    def generate_change_list(self):
        """Serialize the changes in the changememory"""
        change_list = self.changememory.generate()
        #change_list = ChangeList(resources=changes)
        change_list.describedby = self.source.describedby_uri
        change_list.up = self.source.capability_list_uri
        change_list.md_from = change_list.resources[0].timestamp
        change_list.md_until = 'now'
        return change_list.as_xml()

    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.write(self.generate_change_list())
