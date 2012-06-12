"""ResourceSync inventory object

A inventory is a set of resources with some metadata for each 
resource. Comparison of inventorys from a source and a 
destination allows understanding of whether the two are in
sync or whether some resources need to be updated in the
destination.
"""
import sys
import StringIO
from xml.etree.ElementTree import ElementTree, Element, parse

from inventory import Inventory
from client_resource import ClientResource

SITEMAP_NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
RS_NS = 'http://resourcesync.org/change/0.1'

class ClientInventoryIndexError(Exception):
    """Exception indicating attempt to read sitemapindex instead of sitemap"""

    def __init__(self, etree=None):
        self.etree = etree

    def __repr__(self):
        return("Got sitemapindex when expecting sitemap")

class ClientInventory(Inventory):
    """Class representing a inventory of resources

    This same class is used for both the source and the destination
    and is the central point of comparison the decide whether they
    are in sync or what needs to be copied to bring the destinaton
    into sync.

    A inventory will admit only one resource with any given URI.
    """

    def __init__(self, source=None, resources=None):
        self.source=source  # defined by Inventory class, not used here
        self.resources=(resources if (resources is not None) else {})
        self.pretty_xml=False

    def __len__(self):
        return len(self.resources)

    def add(self, resource, replace=False):
        """Add a resource to this inventory

        Will throw a ValueError is the resource (ie. same uri) already
        exists in the inventory, unless replace=True.
        """
        uri = resource.uri
        if (uri in self.resources):
            raise ValueError("Attempt to add resource already in inventory") 
        self.resources[uri]=resource

    def compare(self,src):
        """Compare the current inventory object with the specified inventory

        The parameter src must also be a inventory object, it is assumed
        to be the source, and the current object is the destination. This 
        written to work for any objects in self and sc, provided that the
        == operator can be used to compare them.
        """
        # Sort both self and src so that we can then compare in 
        # sequence
        dst_iter = iter(sorted(self.resources.keys()))
        src_iter = iter(sorted(src.resources.keys()))
        num_same=0
        changed=[]
        deleted=[]
        added=[]
        dst_cur=next(dst_iter,None)
        src_cur=next(src_iter,None)
        while ((dst_cur is not None) and (src_cur is not None)):
            #print 'dst='+dst_cur+'  src='+src_cur
            if (dst_cur == src_cur):
                if (self.resources[dst_cur]==src.resources[src_cur]):
                    num_same+=1
                else:
                    changed.append(dst_cur)
                dst_cur=next(dst_iter,None)
                src_cur=next(src_iter,None)
            elif (not src_cur or dst_cur < src_cur):
                deleted.append(dst_cur)
                dst_cur=next(dst_iter,None)
            elif (not dst_cur or dst_cur > src_cur):
                added.append(src_cur)
                src_cur=next(src_iter,None)
            else:
                raise InternalError("this should not be possible")
        # what do we have leftover in src or dst lists?
        while (dst_cur is not None):
            deleted.append(dst_cur)
            dst_cur=next(dst_iter,None)
        while (src_cur is not None):
            added.append(src_cur)
            src_cur=next(src_iter,None)
        # have now gone through both lists
        return(num_same,changed,deleted,added)

    def has_md5(self):
        """Return true if the inventory has resource entries with md5 data"""
        for r in self.resources.values():
            if (r.md5 is not None):
                return(True)
        return(False)
                
    def as_xml(self, entries=None):
        """Return XML for this inventory in sitemap format
	
	If entries is specified then will write a sitemap that contains only
	the specified entries.
        """
        root = Element('urlset', { 'xmlns': SITEMAP_NS,
                                   'xmlns:rs': RS_NS } )
        if (self.pretty_xml):
            root.text="\n"
        if (entries is None):
	    entries=sorted(self.resources.keys())
        for r in entries:
            e=self.resources[r].etree_element()
            if (self.pretty_xml):
                e.tail="\n"
            root.append(e)
        tree = ElementTree(root);
        xml_buf=StringIO.StringIO()
        if (sys.version_info < (2,7)):
            tree.write(xml_buf,encoding='UTF-8')
        else:
            tree.write(xml_buf,encoding='UTF-8',xml_declaration=True,method='xml')
        return(xml_buf.getvalue())

    def __str__(self):
        return(self.as_xml())

    def parse_xml(self, fh):
        """Parse XML Sitemap from fh and add resources to this inventory object

        Returns the number of resources added. We adopt a very lax approach 
        here. The parsing is properly namespace aware but we search just 
        for the elements wanted and leave everything else alone.

        The one exception is detection of Sitemap indexes. If the root element
        indicates a sitemapindex then a ClientInventoryIndexError() is thrown 
        and the etree passed along with it.
        """
        etree=parse(fh)
        # check root element: urlset (for sitemap), sitemapindex or bad
        if (etree.getroot().tag == '{'+SITEMAP_NS+"}urlset"):
            resources_added=0
            for url_element in etree.findall('{'+SITEMAP_NS+"}url"):
                self.add( ClientResource.from_etree(url_element) )
                resources_added+=1
            return(resources_added)
        elif (etree.getroot().tag == '{'+SITEMAP_NS+"}sitemapindex"):
            raise ClientInventoryIndexError(etree)
        else:
            raise ValueError("XML is not sitemap or sitemapindex")
