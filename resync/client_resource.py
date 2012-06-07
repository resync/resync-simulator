from xml.etree.ElementTree import Element,tostring
import re

from resource import Resource

SITEMAP_NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
RS_NS = 'http://resourcesync.org/change/0.1'      

class ClientResource(Resource):
    """One resource and associated metadta with additions for client"""

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
            self.lastmod=lastmod
        size = etree.findtext('{'+RS_NS+"}size")
        if (size is not None):
            self.size=int(size) #FIXME should throw exception if not number                                      
        md5 = etree.findtext('{'+RS_NS+"}md5")
        if (md5 is not None):
            self.md5=md5
        return(self)
