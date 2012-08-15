#!/usr/bin/env python
# encoding: utf-8
"""
event_log.py: A collection of event logger implementations

Created by Bernhard Haslhofer on 2012-04-24.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

import logging

from observer import Observer

class ConsoleEventLog(Observer):
    """This EventLog logs change events to the console"""
    
    def __init__(self, observable, config=None):
        observable.register_observer(self)
    
    def notify(self, change):
        print "Event: " + str(change)

class FileEventLog(Observer):
    """This EventLog logs change events to a log file"""

    def __init__(self, observable, config=None):
        observable.register_observer(self)
        if config is None:
            logfile = "source_events.log"
        else:
            logfile = config['filename']
        logging.basicConfig(filename=logfile,
                            filemode='w',
                            format='%(asctime)s %(message)s',
                            datefmt='%Y-%m-%dT%H:%M:%S',
                            level=logging.INFO)
                            
    def notify(self, change):
        logging.info(str(change))

