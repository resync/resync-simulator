#!/usr/bin/env python

"""util.py: A collection of utility functions used by the ResourceSync
simulator."""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"


from datetime import datetime
import random

def current_datetime():
    """Returns a nicely formatted date time string"""
    return datetime.now().isoformat('T')

def generate_payload(payload_size):
    """Generates random payload size between 0 and MAX_PAYLOAD_SIZE"""
    return random.randint(0, payload_size)
