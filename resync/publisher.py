#!/usr/bin/env python
# encoding: utf-8
"""
publisher.py: A publisher sends notifications to some external receiver.

Created by Bernhard Haslhofer on 2012-04-24.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

from observer import Observer

class SimplePublisher(Observer):
    """This publisher simply publishes changes to the console"""
    
    def __init__(self, source, config):
        source.register_observer(self)
    
    def notify(self, event):
        print "Sending notification " + str(event)




