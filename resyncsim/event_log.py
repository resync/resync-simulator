#!/usr/bin/env python
# encoding: utf-8
"""
event_log.py: Logs change events to various output channels

Created by Bernhard Haslhofer on 2012-04-24.
Copyright (c) 2012 Cornell University. All rights reserved.
"""

from observer import Observer

class ConsoleEventLog(Observer):
    """This EventLog logs change events to the console"""
    
    def notify(self, event):
        print event

