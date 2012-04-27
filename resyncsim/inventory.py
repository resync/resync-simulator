#!/usr/bin/env python
# encoding: utf-8
"""
inventory.py: Various forms of source inventory implementations

Created by Bernhard Haslhofer on 2012-04-26.
Copyright (c) 2012 Cornell University. All rights reserved.
"""

import tornado.web

class Inventory(object):
    """An inventory knows about a source and produces info about it contents"""
    
    def __init__(self, source):
        self.source = source


class DynamicSiteMapInventory(Inventory):
    """A dynamic sitemap is generated on the fly"""

    def __init__(self, source, config):
        super(DynamicSiteMapInventory, self).__init__(source)
        print "\n*** Instantiated Dynamic SiteMap Generator ***"
        
    @property
    def handler(self):
        return (
            r"/hello", 
            HelloHandler,
            dict(source = self.source),
        )


class HelloHandler(tornado.web.RequestHandler):
    """Resource handler"""

    def initialize(self, source):
            self.source = source


    def get(self):
        self.write("Hello world")

    

