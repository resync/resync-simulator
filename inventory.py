#!/usr/bin/env python

"""inventory.py: A ResourceSync inventory contains a set of resources. This
module contains all inventory-related operations"""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"

import pprint

import util

MAX_PAYLOAD_SIZE = 500


class Resource:
    """A Web Resource"""
    def __init__(self, id, payload):
        self.id = id
        self.payload = payload


class Inventory:
    
    def __init__(self, no_resources):
        """Initializes the resource inventory at startup time"""
        self.current_resources = {} # holds current inventory state (key = id)
        self.deleted_resources = {} # holds deletion history
        self.updated_resources = {} # holds update history
        self.bootstrap_inventory(no_resources)
    
    def bootstrap_inventory(self, no_resources):
        """Fills the inventory with an inital set of resources"""
        for i in range(no_resources):
            self.current_resources[i] = dict(
                                            lm_date = util.current_datetime(),
                                            payload = util.
                                                generate_payload(
                                                MAX_PAYLOAD_SIZE))
        
    
    def print_inventory(self):
        """Prints out the current simulator inventory as string"""
        return pprint.pprint(self.current_resources)
    
    def print_deletion_history(self):
        """Prints the history of deleted resources as string"""
        return pprint.pprint(self.deleted_resources)

    def print_update_history(self):
        """Prints the history of updated resources as string"""
        return pprint.pprint(self.deleted_resources)
