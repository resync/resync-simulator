#!/usr/bin/env python
# encoding: utf-8
"""
resource.py: A URI-identified web resource with some attached resource
representation payload.

For memory-efficency reaons, a resource object only stores:
    * internal identifier (id),
    * last modified date (lastmod),
    * payload size (size).
    
The following properties are generated dynamically at run-time:
    * URI (uri)
    * resource representation string (payload)
    * payload hash (md5) 
"""

import time
from datetime import datetime
import hashlib

class Resource(object):
    __slots__=('id', 'lastmod', 'size')
    
    def __init__(self, id, size):
        self.id = id
        self.lastmod = datetime.now().isoformat('T')
        self.size = size
        
    @property
    def uri(self, base_uri):
        """Constructs the resource uri by appending the internal id to a
        base URI (e.g., http://example.org/resources/)"""
        return base_uri + self.id
        
    @property
    def payload(self):
        """The resource's payload
        
        TODO: implement as defined in
        http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        
        """
        return " ".join([str(self.id) for x in range(self.size)])
    
    @property
    def md5(self):
        """The MD5 computed over the resource payload"""
        return hashlib.md5(self.payload).hexdigest()
        

    def update(self, new_payload_size):
        """Updates resource payload and last modified date"""
        self.lastmod = datetime.now().isoformat('T')
        self.size = new_payload_size
    
    def __str__(self):
        """Prints out the source's resources"""
        return "[%d | %s | %d]" % ( self.id, 
                                    self.lastmod, 
                                    self.size)

# run standalone for testing purposes
if __name__ == '__main__':
    res = Resource(1, 20)
    print res