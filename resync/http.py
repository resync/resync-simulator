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
        
        if self.source.has_inventory:
            if source.inventory.config['class'] == "DynamicSourceInventory":
                self.handlers = self.handlers + \
                    [(r"/%s" % self.source.inventory.path,
                        InventoryHandler, 
                        dict(inventory = self.source.inventory))]
            elif source.inventory.config['class'] == "StaticSourceInventory":
                self.handlers = self.handlers + \
                    [(r"/(sitemap\d*\.xml)",
                        tornado.web.StaticFileHandler,
                        dict(path = self.settings['static_path']))]
        
        if self.source.has_changememory:
            self.handlers = self.handlers + \
                [(r"/%s" % self.source.changememory.url, 
                    DynamicChangeSetHandler,
                    dict(changememory = self.source.changememory)),
                (r"/%s/([0-9]+)/diff" % self.source.changememory.url,
                    DynamicChangeSetDiffHandler,
                    dict(changememory = self.source.changememory))]
            
    
    def run(self):
        print "*** Starting up HTTP Interface on port %i ***\n" % (self.port)
        application = tornado.web.Application(
                        handlers = self.handlers, 
                        debug = True,
                        **self.settings)
        self.http_server = tornado.httpserver.HTTPServer(application)
        self.http_server.listen(self.port)
        tornado.ioloop.IOLoop.instance().start()
        
    def stop(self):
        print "*** Stopping HTTP Interface ***\n"
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
    
    def initialize(self, inventory):
        self.inventory = inventory
    
    @property
    def sitemap(self):
        """Creates a sitemap inventory"""
        self.inventory.generate()
        return Sitemap().inventory_as_xml(self.inventory)
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.write(self.sitemap)

# Changememory Handlers

class DynamicChangeSetHandler(tornado.web.RequestHandler):
    """The HTTP request handler for the DynamicDigest"""

    def initialize(self, changememory):
        self.changememory = changememory
    
    @property
    def next_changeset_uri(self):
        return self.changememory.next_changeset_uri
    
    def current_changeset_uri(self, event_id = None):
        return self.changememory.current_changeset_uri(event_id = event_id)
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.render("changedigest.xml",
                this_changeset_uri = self.current_changeset_uri(),
                next_changeset_uri = self.next_changeset_uri,
                changes = self.changememory.changes)

class DynamicChangeSetDiffHandler(DynamicChangeSetHandler):
    """The HTTP request handler for the DynamicDigest"""
    
    def get(self, event_id):
        self.event_id = event_id
        self.set_header("Content-Type", "application/xml")
        self.render("changedigest.xml",
                this_changeset_uri = self.current_changeset_uri(event_id),
                next_changeset_uri = self.next_changeset_uri,
                changes = self.changememory.changes_from(event_id))
