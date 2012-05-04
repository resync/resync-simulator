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
    """An abstract change memory implementation that doesn't do anything.
    ChangeMemory implementations can extend this class
    """
    
    def __init__(self, source):
        self.source = source
        source.register_observer(self)

# A dynamic in-memory change digest

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
        print self.changes
        self.render("change_digest.xml",
                    changes = self.changes)


# A dynamic change digest that implements client-driven paging                    

class DynamicPagingDigest(ChangeMemory):
    """A change memory that stores changes in an in-memory list"""

    def __init__(self, source, config):
        super(DynamicPagingDigest, self).__init__(source)
        self.url = config['url']
        self.changes = []
        
    def notify(self, event):
        """Simply store a change in the in-memory list"""
        self.changes.append(event)
    
    @property
    def handlers(self):
        return [(r"/changes", 
                DynamicPagingDigestHandler,
                dict(changes = self.changes)),
                (r"/changes/([0-9]+)/diff",
                PartialDynamicPagingDigestHandler,
                dict(changes = self.changes)),
        ]
        

class DynamicPagingDigestHandler(tornado.web.RequestHandler):
    """The HTTP request handler for the DynamicPagingDigest"""

    def initialize(self, changes):
        self.changes = changes

    def get(self):
        self.set_header("Content-Type", "application/xml")
        self.render("change_digest_paging.xml",
                    changes = self.changes)

class PartialDynamicPagingDigestHandler(tornado.web.RequestHandler):
    """The HTTP request handler for the DynamicPagingDigest"""

    def initialize(self, changes):
        self.changes = changes

    def get(self, seqId):
        self.set_header("Content-Type", "application/xml")
        self.render("change_digest_paging_partial.xml",
                    last_seq_id = int(seqId),
                    changes = self.changes)




        
