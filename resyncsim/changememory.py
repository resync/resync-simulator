#!/usr/bin/env python
# encoding: utf-8
"""
changememory.py: A collection of change memory implementations

Created by Bernhard Haslhofer on 2012-04-27.
Copyright (c) 2012 Cornell University. All rights reserved.
"""

import tornado.web

from observer import Observer

class ChangeMemory(Observer):
    """An change memory keeps track of changes"""
    
    def __init__(self, source):
        self.source = source
        source.register_observer(self)


class SimpleChangeMemory(ChangeMemory):
    """A change memory that stores changes in an in-memory list"""

    def __init__(self, source, config):
        super(SimpleChangeMemory, self).__init__(source)
        self.url = config['url']
        self.changes = []
        
    def notify(self, event):
        """Simply store a change in the in-memory list"""
        self.changes.append(event)
    
    @property
    def handler(self):
        return (
            r"%s" % self.url, 
            SimpleChangeMemoryHandler,
            dict(changes = self.changes),
        )


class SimpleChangeMemoryHandler(tornado.web.RequestHandler):
    """The HTTP request handler for the SimpleChangeMemory"""

    def initialize(self, changes):
        self.changes = changes
    
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(self.changes))
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.render("sitemap_changes.xml",
                    changes = self.changes)

