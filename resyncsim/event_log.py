#!/usr/bin/env python
# encoding: utf-8
"""
event_log.py: A collection of event logger implementations

Created by Bernhard Haslhofer on 2012-04-24.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

from observer import Observer

class ConsoleEventLog(Observer):
    """This EventLog logs change events to the console"""
    
    def __init__(self, source, config):
        source.register_observer(self)
    
    def notify(self, event):
        print event

