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

from resync.sitemap import Sitemap
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
            (r"/", HomeHandler, dict(source = self.source)),
            (r"%s" % Source.RESOURCE_PATH, ResourcesHandler,
                                dict(source = self.source)),
            (r"%s/([0-9]+)" % Source.RESOURCE_PATH, ResourceHandler,
                                dict(source = self.source)),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
                                dict(path = self.settings['static_path'])),
        ]

        """Initialize resource_list handlers"""
        if self.source.has_resource_list_builder:
            resource_list_builder = self.source.resource_list_builder
            if resource_list_builder.config['class'] == "DynamicResourceListBuilder":
                self.handlers = self.handlers + \
                    [(r"/%s" % resource_list_builder.path,
                        ResourceListHandler, 
                        dict(resource_list_builder = resource_list_builder))]
            elif resource_list_builder.config['class'] == "StaticResourceListBuilder":
                self.handlers = self.handlers + \
                    [(r"/(sitemap\d*\.xml)",
                        tornado.web.StaticFileHandler,
                        dict(path = self.settings['static_path']))]
        
        """Initialize changememory handlers"""
        if self.source.has_changememory:
            changememory = self.source.changememory
            if changememory.config['class'] == "DynamicChangeList":
                self.handlers = self.handlers + \
                    [(r"/%s" % changememory.uri_path, 
                        DynamicChangeListHandler,
                        dict(changememory = changememory)),
                    (r"/%s/from/([0-9]+)" % changememory.uri_path,
                        DynamicChangeListDiffHandler,
                        dict(changememory = changememory))]
            elif changememory.config['class'] == "StaticChangeList":
                self.handlers = self.handlers + \
                    [(r"/%s/%s" % (changememory.uri_path, 
                                    changememory.uri_file), 
                        StaticChangeListHandler,
                        dict(changememory = changememory)),
                    (r"/%s/(changelist\d*\.xml)" % changememory.uri_path,
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

class ResourcesHandler(BaseRequestHandler):
    """Resources subset selection handler"""
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

# ResourceList Handlers
            
class ResourceListHandler(tornado.web.RequestHandler):
    """The HTTP request handler for the ResourceList"""
    
    def initialize(self, resource_list_builder):
        self.resource_list_builder = resource_list_builder
    
    def generate_sitemap(self):
        """Creates a resource_list"""
        resource_list = self.resource_list_builder.generate()
        return Sitemap().resources_as_xml(resource_list,
                                        capabilities=resource_list.capabilities)
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.write(self.generate_sitemap())

# Changememory Handlers

class DynamicChangeListHandler(tornado.web.RequestHandler):
    """The HTTP request handler for dynamically generated changelists"""

    def initialize(self, changememory):
        self.changememory = changememory
    
    def generate_changelist(self, changeid=None):
        """Serialize the changes in the changememory"""
        changelist = self.changememory.generate(from_changeid=changeid)
        return Sitemap().resources_as_xml(changelist)
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.write(self.generate_changelist())

class DynamicChangeListDiffHandler(DynamicChangeListHandler):
    """The HTTP request handler for the dynamically generated sub-changelists"""
    
    def get(self, changeid):
        changeid = int(changeid)
        if changeid > self.changememory.latest_change_id:
            self.send_error(status_code = 404)
        elif not self.changememory.knows_changeid(changeid):
            self.send_error(status_code = 410)
        else:
            self.set_header("Content-Type", "application/xml")
            self.write(self.generate_changelist(changeid=changeid))
            
class StaticChangeListHandler(tornado.web.RequestHandler):
    """The HTTP request handler for static changelists"""
    
    def initialize(self, changememory):
        self.changememory = changememory
        
    def generate_changelist(self):
        "Serialize the changes in the changememory"
        changelist = self.changememory.generate()
        return Sitemap().resources_as_xml(changelist, 
                                        capabilities=changelist.capabilities)
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.write(self.generate_changelist())
