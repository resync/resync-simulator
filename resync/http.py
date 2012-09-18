#!/usr/bin/env python
# encoding: utf-8
"""
http.py: The source's HTTP Web interface running on the
non-blocking Tornado web server (http://www.tornadoweb.org/)

Created by Bernhard Haslhofer on 2012-04-24.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

import threading
import os.path
import logging

import tornado.httpserver
import tornado.ioloop
import tornado.web

from resync.source import Source
from resync.sitemap import Sitemap


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
            (r"/", HomeHandler, dict(source = self.source)),
            (r"%s" % Source.RESOURCE_PATH, ResourceListHandler,
                                dict(source = self.source)),
            (r"%s/([0-9]+)" % Source.RESOURCE_PATH, ResourceHandler,
                                dict(source = self.source)),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
                                dict(path = self.settings['static_path'])),
        ]
        
        """Initialize inventory handlers"""
        if self.source.has_inventory_builder:
            inventory_builder = self.source.inventory_builder
            if inventory_builder.config['class'] == "DynamicInventoryBuilder":
                self.handlers = self.handlers + \
                    [(r"/%s" % inventory_builder.path,
                        InventoryHandler, 
                        dict(inventory_builder = inventory_builder))]
            elif inventory_builder.config['class'] == "StaticInventoryBuilder":
                self.handlers = self.handlers + \
                    [(r"/(sitemap\d*\.xml)",
                        tornado.web.StaticFileHandler,
                        dict(path = self.settings['static_path']))]
        
        """Initialize changememory handlers"""
        if self.source.has_changememory:
            changememory = self.source.changememory
            if changememory.config['class'] == "DynamicChangeSet":
                self.handlers = self.handlers + \
                    [(r"/%s" % changememory.uri_path, 
                        DynamicChangeSetHandler,
                        dict(changememory = changememory)),
                    (r"/%s/from/([0-9]+)" % changememory.uri_path,
                        DynamicChangeSetDiffHandler,
                        dict(changememory = changememory))]
            elif changememory.config['class'] == "StaticChangeSet":
                self.handlers = self.handlers + \
                    [(r"/%s/%s" % (changememory.uri_path, 
                                    changememory.uri_file), 
                        StaticChangeSetHandler,
                        dict(changememory = changememory)),
                    (r"/%s/(changeset\d*\.xml)" % changememory.uri_path,
                        tornado.web.StaticFileHandler,
                        dict(path = self.settings['static_path']))]
    
    def run(self):
        self.logger.info("Starting up HTTP Interface on port %i" % (self.port))
        application = tornado.web.Application(
                        handlers = self.handlers, 
                        debug = True,
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
                    resource_count = self.source.resource_count,
                    source = self.source)

# Resource Handlers

class ResourceListHandler(BaseRequestHandler):
    """Resource list selection handler"""
    def get(self):
        rand_res = sorted(self.source.random_resources(100), 
            key = lambda res: int(res.basename))
        self.render("resource.index.html", resources = rand_res)
                        

class ResourceHandler(BaseRequestHandler):
    """Resource handler"""
    def get(self, basename):
        resource = self.source.resource(basename)
        if resource == None:
            self.send_error(404)
        else:
            self.set_header("Content-Type", "text/plain")
            self.set_header("Content-Length", resource.size)
            self.set_header("Last-Modified", resource.lastmod)
            self.set_header("Etag", "\"%s\"" % resource.md5)
            payload = self.source.resource_payload(basename)
            self.write(payload)

# Inventory Handlers
            
class InventoryHandler(tornado.web.RequestHandler):
    """The HTTP request handler for the Inventory"""
    
    def initialize(self, inventory_builder):
        self.inventory_builder = inventory_builder
    
    def generate_sitemap(self):
        """Creates a sitemap inventory"""
        inventory = self.inventory_builder.generate()
        return Sitemap().resources_as_xml(inventory,
                                        capabilities=inventory.capabilities)
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.write(self.generate_sitemap())

# Changememory Handlers

class DynamicChangeSetHandler(tornado.web.RequestHandler):
    """The HTTP request handler for dynamically generated changesets"""

    def initialize(self, changememory):
        self.changememory = changememory
    
    def generate_changeset(self, changeid=None):
        """Serialize the changes in the changememory"""
        changeset = self.changememory.generate(from_changeid=changeid)
        return Sitemap().resources_as_xml(changeset)
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.write(self.generate_changeset())

class DynamicChangeSetDiffHandler(DynamicChangeSetHandler):
    """The HTTP request handler for the dynamically generated sub-changesets"""
    
    def write_error(self, status_code, **kwargs):
        self.write("Error %d - %s" % (status_code, kwargs['message']))
    
    def get(self, changeid):
        changeid = int(changeid)
        self.set_header("Content-Type", "application/xml")
        self.write(self.generate_changeset(changeid=changeid))
            
class StaticChangeSetHandler(tornado.web.RequestHandler):
    """The HTTP request handler for static changesets"""
    
    def initialize(self, changememory):
        self.changememory = changememory
        
    def generate_changeset(self):
        "Serialize the changes in the changememory"
        changeset = self.changememory.generate()
        return Sitemap().resources_as_xml(changeset, 
                                        capabilities=changeset.capabilities)
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.write(self.generate_changeset())