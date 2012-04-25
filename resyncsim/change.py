#!/usr/bin/env python
# encoding: utf-8
"""
change.py: A model for expressing change.

Created by Bernhard Haslhofer on 2012-04-24.
Copyright (c) 2012 Cornell University. All rights reserved.
"""

import time
from datetime import datetime


class ChangeEvent(object):
    """A Change Event carries a type, a timestamp and the affected
    resource"""

    def __init__(self, event_type, resource):
        self.event_type = event_type
        self.resource = resource

    def __str__(self):
        return str([self.event_type, str(self.resource)])