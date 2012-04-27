#!/usr/bin/env python
# encoding: utf-8
"""
http.py: The source's HTTP Web interface running on the
non-blocking Tornado web server (http://www.tornadoweb.org/)

"""

import threading
import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.web


class HTTPInterface(threading.Thread):
    """The repository's HTTP interface. To make sure it doesn't interrupt
    the simulation, it runs in a separate thread.
    
    http://stackoverflow.com/questions/323972/
        is-there-any-way-to-kill-a-thread-in-python (Stoppable Threads)
        
    http://www.slideshare.net/juokaz/
        restful-web-services-with-python-dynamic-languages-conference
    
    """
    
    def __init__(self, source, port = 8888):
        """Initializes HTTP interface with default settings and handlers"""
        super(HTTPInterface, self).__init__()
        self._stop = threading.Event()
        self.source = source
        self.port = port
        self.settings = dict(
            title=u"ResourceSync Change Simulator",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            autoescape=None,        
        )
        self.handlers = [
            (r"/", HomeHandler, dict(source = self.source)),
            (r"/resources/?", ResourceListHandler, dict(source = self.source)),
            (r"/resources/([0-9]+)", ResourceHandler, dict(source = self.source)),
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
                 dict(path=self.settings['static_path'])),
        ]
    
    
    def add_handlers(self, handlers):
        """Adds a handler to the http interface"""
        self.handlers = self.handlers + handlers
        

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
    

class HomeHandler(tornado.web.RequestHandler):
    """Base URI handler"""
    def initialize(self, source):
            self.source = source
    
    def get(self):
        self.render("home.html",
                    resource_count = len(self.source.resources),
                    config = self.source.config)
        

class ResourceListHandler(tornado.web.RequestHandler):
    """Resource list selection handler"""
    def initialize(self, source):
            self.source = source
    
    def get(self):
        rand_res = sorted(self.source.random_resources(100), 
            key = lambda res: res.id)
        self.render("resource.index.html", resources = rand_res)
                        

class ResourceHandler(tornado.web.RequestHandler):
    """Resource handler"""
    def initialize(self, source):
            self.source = source

    def get(self, res_id):
        res_id = int(res_id)
        if res_id not in self.source.resources.keys():
            self.send_error(404)
        
        resource = self.source.resources[res_id]
        self.render("resource.show.html", resource = resource)
        