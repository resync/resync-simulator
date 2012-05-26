#!/usr/bin/env python
# encoding: utf-8
"""
resource.py: A URI-identified Web resource.
"""

import time
from datetime import datetime
from hashlib import md5

def compute_md5(payload):
    """Compute MD5 over a some payload"""
    return md5(payload).hexdigest()

class Resource(object):
    __slots__=('uri', 'timestamp', 'size', 'md5')
    
    def __init__(self, uri, timestamp = None, size = None, md5 = None):
        self.uri = uri
        self.timestamp = timestamp
        self.size = size
        self.md5 = md5
            
    @property
    def lastmod(self):
        """The Last-Modified data in ISO8601 syntax"""
        if self.timestamp == None: return None
        return datetime.fromtimestamp(self.timestamp).isoformat()
            
    def __str__(self):
        """Prints out the source's resources"""
        return "[%s | %s | %d | %s]" % (self.uri, self.lastmod, self.size,
                                        self.md5)

# run standalone for testing purposes
if __name__ == '__main__':
    res = Resource(uri = "http://example.com/test/1", timestamp = 1234, 
                    size = 500)
    print res