#!/usr/bin/env python
# encoding: utf-8
"""
resource.py: A web resource with dynamically generated payload

Created by Bernhard Haslhofer on 2012-05-08.
"""

import time
from datetime import datetime
import hashlib

class Resource(object):
    """A resource has an identifier, a last modified date, and a payload of
    a certain size."""
    
    def __init__(self, id, payload_size):
        self.id = id
        self.lm_date = datetime.now().isoformat('T')
        self.payload_size = payload_size
        
    def update(self, new_payload_size):
        """Updates resource payload and last modified date"""
        self.lm_date = datetime.now().isoformat('T')
        self.payload_size = new_payload_size
        
    def uri(self, base_uri):
        """Constructs the resource uri by appending the internal id to a
        base URI (e.g., http://example.org/resources/)"""
        return base_uri + self.identifier
        
    @property
    def payload(self):
        """The resource's payload
        
        TODO: implement as defined in
        http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        
        """
        return " ".join([str(self.id) for x in range(self.payload_size)])
    
    @property
    def md5(self):
        """The MD5 computed over the resource payload"""
        return hashlib.md5(self.payload).hexdigest()
        
    
    
    def __str__(self):
        """Prints out the source's resources"""
        return "[%d | %s | %d]" % ( self.id, 
                                    self.lm_date, 
                                    self.payload_size)