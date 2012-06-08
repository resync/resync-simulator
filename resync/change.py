#!/usr/bin/env python
# encoding: utf-8
"""
change.py: A model for expressing change.

Created by Bernhard Haslhofer on 2012-04-24.
Copyright 2012, ResourceSync.org. All rights reserved.
"""

import time
from datetime import datetime


class ChangeEvent(object):
    """A Change Event carries an event identifier, a type, a timestamp and
    the affected resource"""

    def __init__(self, event_type, resource):
        self.event_type = event_type
        self.resource = resource
        self.event_id = -1 # default if not set

    def __str__(self):
        return str([self.event_type, str(self.resource)])