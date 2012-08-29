"""Information about a web resource

Each web resource is identified by a URI and may optionally have
other metadata such as timestamp, size, md5. The lastmod property
provides ISO8601 format string access to the timestamp.

The timestamp is assumed to be stored in UTC.
"""

import time
from calendar import timegm
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
        """The Last-Modified data in ISO8601 syntax, Z notation

        The lastmod is stored as unix timestamp which is already
        in UTC."""
        if (self.timestamp is None):
            return None
        return datetime.utcfromtimestamp(self.timestamp).isoformat() + 'Z'

    @lastmod.setter
    def lastmod(self, lastmod):
        """Set timestamp from an W3C Datetime Last-Modified value

        The sitemaps.org specification says that <lastmod> values
        must comply with the W3C Datetime format 
        (http://www.w3.org/TR/NOTE-datetime). This is a restricted
        subset of ISO8601. In particular, all forms that include a 
        time must include a timezone indication so there is no
        notion of local time (which would be tricky on the web). The
        forms allowed are:

        Year:
          YYYY (eg 1997)
        Year and month:
          YYYY-MM (eg 1997-07)
        Complete date:
          YYYY-MM-DD (eg 1997-07-16)
        Complete date plus hours and minutes:
          YYYY-MM-DDThh:mmTZD (eg 1997-07-16T19:20+01:00)
        Complete date plus hours, minutes and seconds:
          YYYY-MM-DDThh:mm:ssTZD (eg 1997-07-16T19:20:30+01:00)
        Complete date plus hours, minutes, seconds and a decimal fraction 
        of a second
          YYYY-MM-DDThh:mm:ss.sTZD (eg 1997-07-16T19:20:30.45+01:00)
        where:
          TZD  = time zone designator (Z or +hh:mm or -hh:mm)

        We do not anticipate the YYYY and YYYY-MM forms being used but
        interpret them as YYYY-01-01 and YYYY-MM-01 respectively. All
        dates are interpreted as having time 00:00:00.0 UTC.

        Datetimes not specified to the level of seconds are intepreted
        as 00.0 seconds.
        """
        if (lastmod is None):
            self.timestamp = None
            return
        if (lastmod == ''):
            raise ValueError('Attempt to set empty lastmod')
        # Make a date into a full datetime
        m = re.match(r"\d\d\d\d(\-\d\d(\-\d\d)?)?$",lastmod)
        if (m is not None):
            if (m.group(1) is None):
                lastmod += '-01-01'
            elif (m.group(2) is None):
                lastmod += '-01'
            lastmod += 'T00:00:00Z'
        # Now have datetime with timezone info
        m = re.match(r"(.*\d{2}:\d{2}:\d{2})(\.\d+)([^\d].*)?$",lastmod)
        # Chop out fractional seconds
        fractional_seconds = 0
        if (m is not None):
            lastmod = m.group(1)
            if (m.group(3) is not None):
                lastmod += m.group(3)
            fractional_seconds = float(m.group(2))
        # Now check that only allowed formats supplied (the parse
        # function is rather lax)
        m = re.match(r"\d\d\d\d\-\d\d\-\d\dT\d\d:\d\d(:\d\d)?(Z|[+-]\d\d:\d\d)$",lastmod)
        if (m is None):
            raise ValueError("Bad lastmod format (%s)" % lastmod)
        dt = dateutil_parser.parse(lastmod)
        # timetuple ignores timezone information
        #offset_seconds = dt.tzinfo.utcoffset(0).total_seconds() #only >=2.7
        offset = dt.tzinfo.utcoffset(0)
        offset_seconds = (offset.seconds + offset.days * 24 * 3600)
        self.timestamp = timegm(dt.timetuple()) + offset_seconds + fractional_seconds

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
        return "[ %s | %s | %s | %s]" % (self.uri, self.lastmod, 
                                         str(self.size), self.md5)
                                         
    def __repr__(self):
        """Return an unambigous representation"""
        dict_repr = dict((name, getattr(self, name)) 
                    for name in dir(self) if not (name.startswith('__') 
                                                        or name == 'equal')) 
        return str(dict_repr)
        
