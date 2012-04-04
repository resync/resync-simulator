#!/usr/bin/env python
# encoding: utf-8
"""
web_interface.py: The simulator's HTTP Web interface running on the
non-blocking Tornado web server (http://www.tornadoweb.org/)

"""

import threading

import tornado.httpserver
import tornado.ioloop
import tornado.web


class HTTPInterface(threading.Thread):
    """This class makes sure that the HTTP interface runs within a stoppable
    thread as discussed here:
    
    http://stackoverflow.com/questions/323972/
        is-there-any-way-to-kill-a-thread-in-python
    
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
        handlers = [
            (r"/", HomeHandler)
        ]
        tornado.web.Application.__init__(self, handlers, debug = True)
        self.inventory = inventory
        

class BaseHandler(tornado.web.RequestHandler):
    @property
    def inventory(self):
        return self.application.inventory
        

class HomeHandler(BaseHandler):
    def get(self):
        self.write("bla")
        self.flush()