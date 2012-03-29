#!/usr/bin/env python

"""inventory.py: A ResourceSync inventory contains a set of resources. This
module contains all inventory-related operations"""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"

import pprint
import random

import util

MAX_PAYLOAD_SIZE = 500

class Inventory:
    
    def __init__(self):
        """Initializes the resource inventory at startup time"""
        self.current_resources = {} # current inventory
        self.deleted_resources = {} # holds deletion history
        self.updated_resources = {} # holds update history
        self.max_res_id = 0
    
    def bootstrap(self, no_resources):
        """Fills the inventory with an inital set of resources"""
        for i in range(no_resources): self.create_resource()
    
    def select_random_resource(self):
        """Selects a random resource id from the inventory"""
        return random.choice(self.current_resources.keys())
    
    def create_resource(self, res_id = None):
        """Creates a new resource and adds it to the inventory"""
        res = dict(
            lm_date = util.current_datetime(), \
            payload_size = util.generate_payload(MAX_PAYLOAD_SIZE)
        )
        if res_id == None:
            self.current_resources[self.max_res_id] = res
            self.max_res_id += 1
        else:
            self.current_resources[res_id] = res
    
    def update_resource(self, res_id):
        """Updates a resource with given a given resource id"""
        # TODO: use update list
        self.updated_resources[res_id] = self.current_resources[res_id]
        self.delete_resource(res_id)
        self.create_resource(res_id)
        
    def delete_resource(self, res_id):
        """Deletes a resource with a given resource id"""
        self.deleted_resources[res_id] = self.current_resources[res_id]
        del self.current_resources[res_id]
    
    # Inventory serialization functions
    
    def __str__(self):
        """Prints out the current simulator inventory as string"""
        cr = "INVENTORY:\n" + pprint.pformat(self.current_resources)
        dr = "DELETED RESOURCES:\n" + pprint.pformat(self.deleted_resources)
        ur = "UPDATED RESOURCES:\n" + pprint.pformat(self.updated_resources)
        return cr + "\n" + dr + "\n" + ur
        
        
    def to_sitemap(self):
        """Serializes the inventory to a sitemap"""
        pass