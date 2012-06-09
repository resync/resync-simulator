#!/usr/bin/env python
# encoding: utf-8
"""
inventory.py: An inventory is a set of resources provided by some source.

Created by Bernhard Haslhofer on 2012-04-26.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

class Inventory(object):
    """An inventory knows about the source for getting its resources"""
    
    def __init__(self, source):
        self.source = source
        

class DynamicSiteMap(Inventory):
    """An inventory that simply takes all resources from a source"""

    def __init__(self, source, config):
        super(DynamicSiteMap, self).__init__(source)
        self.config = config
        print "\n*** Instantiated Dynamic SiteMap Generator ***"
        
    @property
    def resources(self):
        """The resources are provided by the source"""
        return self.source.resources

    def to_sitemap(self):
        """Returns a Sitemap serialization of the inventory"""
        return NotImplemented