from time import mktime
from datetime import datetime
from xml.etree.ElementTree import Element,tostring
import re

from resource import Resource

SITEMAP_NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
RS_NS = 'http://resourcesync.org/change/0.1'      

class ClientResource(Resource):
    """One resource and associated metadta with additions for client"""

    def __init__(self, uri=None, timestamp = None, size = None, md5 = None,
                       lastmod = None):
        self.uri = uri
        self.timestamp = timestamp
        self.size = size
        self.md5 = md5
        if (lastmod is not None):
            self.set_lastmod(lastmod)

    def set_lastmod(self,lastmod):
        """Set timestamp from an ISO8601 lastmod

        FIXME - should be rolled into resource.py as a setter

        Accepts either seconds or fractional seconds forms of
        an ISO8601 datetime. These are distinguished by checking
        for the presence of a decimal point in the string.
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
        if (self.timestamp is None):
            raise "FIXME - failed to get timestamp"

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
        #print 'eq: self='+self.uri+'  other='+other.uri
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

    def etree_element(self):
        """Return xml.etree.ElementTree.Element representing this resource

        Returns and element for this resource, of the form <url> with 
        enclosed properties that are based on the sitemap with extensions
        for ResourceSync.
        """
        e = Element('url')
        sub = Element('loc', {})
        sub.text=self.uri
        e.append(sub)
        if (self.timestamp is not None):
            sub = Element( 'lastmod', {} )
            sub.text = str(self.lastmod) #ISO8601
            e.append(sub)
        if (self.size is not None):
            sub = Element( 'rs:size', {} )
            sub.text = str(self.size)
            e.append(sub)
        if (self.md5 is not None):
            sub = Element( 'rs:md5', {} )
            sub.text = str(self.md5)
            e.append(sub)
        return(e)

    def as_xml(self,indent=' '):
        """Write out this resource as part of an XML sitemap

        FIXME - can we use existing sitemap module for this?
        FIXME - how do we handle the case of >50k where multiple sitemaps
        are required?
        """
        e = self.etree_element()
        return(tostring(e, encoding='UTF-8')) #must not specify method='xml' in python2.6

    def __str__(self):
        return(self.as_xml())

    @classmethod
    def from_etree(class_, etree):
        """Construct a Resource from an etree

        The parsing is properly namespace aware but we search just for the elements
        wanted and leave everything else alone. Provided there is a <loc> element then
        we'll go ahead and extract as much as possible.
        """
        loc = etree.findtext('{'+SITEMAP_NS+"}loc")
        if (loc is None):
            raise "FIXME - error from no location, should be a proper exceoption class"
        # We at least have a URI, make this object
        self=class_(uri=loc)
        # and then proceed to look for other resource attributes                               
        lastmod = etree.findtext('{'+SITEMAP_NS+"}lastmod")
        if (lastmod is not None):
            self.set_lastmod(lastmod)
        size = etree.findtext('{'+RS_NS+"}size")
        if (size is not None):
            self.size=int(size) #FIXME should throw exception if not number                                      
        md5 = etree.findtext('{'+RS_NS+"}md5")
        if (md5 is not None):
            self.md5=md5
        return(self)
