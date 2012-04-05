#!/usr/bin/env python
# encoding: utf-8
"""
web_interface.py: The simulator's HTTP Web interface running on the
non-blocking Tornado web server (http://www.tornadoweb.org/)



"""

import threading
import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.web


class HTTPInterface(threading.Thread):
    """This class makes sure that the HTTP interface runs within a stoppable
    thread as discussed here:
    
    \cite:
    
    http://stackoverflow.com/questions/323972/
        is-there-any-way-to-kill-a-thread-in-python (Stoppable Threads)
        
    http://www.slideshare.net/juokaz/
        restful-web-services-with-python-dynamic-languages-conference
    
    """
    
    def __init__(self, inventory):
        super(HTTPInterface, self).__init__()
        self._stop = threading.Event()
        self.inventory = inventory
    
    def run(self):
        print "*** Starting up HTTP Interface ***\n"
        application = Application(inventory = self.inventory)
        self.http_server = tornado.httpserver.HTTPServer(application)
        self.http_server.listen(8888)
        tornado.ioloop.IOLoop.instance().start()
        
    def stop(self):
        print "*** Stopping HTTP Interface ***\n"
        tornado.ioloop.IOLoop.instance().stop()
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    

class Application(tornado.web.Application):
    
    def __init__(self, inventory):
        print "File: %s" % __file__
        handlers = [
            (r"/", HomeHandler),
            (r"/resources/(.*)", ResourceHandler),
        ]
        settings = dict(
            title=u"ResourceSync Change Simulator",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            #ui_modules={"Entry": EntryModule},
            autoescape=None,        
        )
        tornado.web.Application.__init__(self, handlers, debug = True, **settings)
        self.inventory = inventory
        

class BaseHandler(tornado.web.RequestHandler):
    @property
    def inventory(self):
        return self.application.inventory
        

class HomeHandler(BaseHandler):
    def get(self):
        resource_count = dict(
            current = len(self.inventory.current_resources),
            updated = len(self.inventory.updated_resources),
            deleted = len(self.inventory.deleted_resources),
        )
        self.render("home.html", resource_count = resource_count)
        
class ResourceHandler(BaseHandler):
    def get(self, slug):
        print slug
        if slug == "":
            self.render("resource.index.html", 
                        list_name = "Current Resources",
                        resources = self.inventory.current_resources)
        elif slug == "updated":
            self.render("resource.index.html", 
                        list_name = "Updated Resources",
                        resources = self.inventory.updated_resources)
        elif slug == "deleted":
            self.render("resource.index.html", 
                        list_name = "Deleted Resources",
                        resources = self.inventory.deleted_resources)