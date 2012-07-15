"""Information about a web resource

Each web resource is identified by a URI and may optionally have
other metadata such as timestamp, size, md5. The lastmod property
provides ISO8601 format string access to the timestamp.
"""

from time import mktime
from datetime import datetime
from dateutil import parser as dateutil_parser
import re
from urlparse import urlparse
from posixpath import basename

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
        # FIXME - need to find a single module that will parse the range
        # of ISO8601 dates required. See test cases in resync/test/test_resource.py.
        # The only problems with dateutils are lack of support for fractions of
        # a second and acceptance of empty string so we fudge these here:
        if (lastmod == ''):
            raise ValueError('Attempt to set empty lastmod')
        fractional_seconds = 0
        m = re.match(r"(.*\d{2}:\d{2}:\d{2})\.(\d+)([^\d].*)?$",lastmod)
        if (m is not None):
            lastmod = m.group(1)
            if (m.group(3) is not None):
                lastmod += m.group(3)
            fractional_seconds = float("0."+m.group(2))
        self.timestamp = mktime(dateutil_parser.parse(lastmod).timetuple()) + fractional_seconds

    @property
    def basename(self):
        """The resource basename (http://example.com/resource/1 -> 1)"""
        parse_object = urlparse(self.uri)
        return basename(parse_object.path)

    def __eq__(self,other):
        """Equality test for resources allowing <1s difference in timestamp"""
        return( self.equal(other,delta=1.0) )

    def equal(self,other,delta=0.0):
        """Equality or near equality test for resources
        
        Equality means:
        1. same uri, AND
        2. same timestamp WITHIN delta if specified for either, AND
        3. same md5 if specified for both, AND
        4. same size if specified for both
        """
        if (other is None): return False
        
        if (self.uri != other.uri):
            return(False)
        if ( self.timestamp is not None or other.timestamp is not None ):
            # not equal if only one timestamp specified
            if ( self.timestamp is None or 
                 other.timestamp is None or
                 abs(self.timestamp-other.timestamp)>=delta ):
                return(False)
        if ( ( self.md5 is not None and other.md5 is not None ) and
             self.md5 != other.md5 ):
            return(False)
        if ( ( self.size is not None and other.size is not None ) and
             self.size != other.size ):
            return(False)
        return(True)
    
    def __str__(self):
        """Return a human readable string for this resource"""
        return "[%s | %s | %s | %s]" % (self.uri, self.lastmod, 
                                        str(self.size), self.md5)
