#!/usr/bin/env python
# encoding: utf-8
"""
changememory.py: A collection of change memory implementations

Created by Bernhard Haslhofer on 2012-04-27.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

import tornado.web

from observer import Observer

class ChangeMemory(Observer):
    """An change memory keeps track of changes"""
    
    def __init__(self, source):
        self.source = source
        source.register_observer(self)


class DynamicDigest(ChangeMemory):
    """A change memory that stores changes in an in-memory list"""

    def __init__(self, source, config):
        super(DynamicDigest, self).__init__(source)
        self.url = config['url']
        self.changes = []
        
    def notify(self, event):
        """Simply store a change in the in-memory list"""
        self.changes.append(event)
    
    @property
    def handlers(self):
        return [(r"%s" % self.url, 
         DynamicDigestHandler,
         dict(changes = self.changes))
        ]


class DynamicDigestHandler(tornado.web.RequestHandler):
    """The HTTP request handler for the DynamicDigest"""

    def initialize(self, changes):
        self.changes = changes
    
    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.render("change_digest.xml",
                    changes = self.changes)