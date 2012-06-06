#!/usr/bin/env python
# encoding: utf-8
"""
resource.py: A URI-identified Web resource.
"""

from time import mktime
from datetime import datetime
from hashlib import md5

from urlparse import urlparse
from posixpath import basename


def compute_md5(payload):
    """Compute MD5 over a some payload"""
    return md5(payload).hexdigest()

class Resource(object):
    __slots__=('uri', 'timestamp', 'size', 'md5')
    
    def __init__(self, uri, timestamp = None, size = None, md5 = None,
                 lastmod = None):
        self.uri = uri
        self.timestamp = timestamp
        self.size = size
        self.md5 = md5
        if (lastmod is not None):
            self.lastmod=lastmod
            
    @property
    def lastmod(self):
        """The Last-Modified data in ISO8601 syntax"""
        if self.timestamp == None: return None
        return datetime.fromtimestamp(self.timestamp).isoformat()

    @lastmod.setter
    def lastmod(self, lastmod):
        """Set timestamp from an ISO8601 Last-Modified value

        Accepts either seconds or fractional seconds forms of
        an ISO8601 datetime. These are distinguished by checking
        for the presence of a decimal point in the string. Will raise
        a ValueError in the case of bad input.
        """
        if (lastmod is None):
            self.timestamp = None
            return
        if (lastmod.find('.')>=0):
            dt = datetime.strptime(lastmod, "%Y-%m-%dT%H:%M:%S.%f" )
        elif (lastmod.find('T')>=0):
            dt = datetime.strptime(lastmod, "%Y-%m-%dT%H:%M:%S" )
        else:
            dt = datetime.strptime(lastmod, "%Y-%m-%d" )
        self.timestamp = mktime(dt.timetuple()) + dt.microsecond/1000000.0

    @property
    def basename(self):
        """The resource basename (http://example.com/resource/1 -> 1)"""
        parse_object = urlparse(self.uri)
        return basename(parse_object.path)
    
    def __str__(self):
        """Prints out the source's resources"""
        return "[%s | %s | %d | %s]" % (self.uri, self.lastmod, self.size,
                                        self.md5)

# run standalone for testing purposes
if __name__ == '__main__':
    res = Resource(uri = "http://example.com/test/1", timestamp = 1234, 
                    size = 500)
    print res
