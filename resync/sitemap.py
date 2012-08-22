"""Read and write ResourceSync inventories and changeset as sitemaps"""

import re
import os
import sys
import logging
from urllib import URLopener
from xml.etree.ElementTree import ElementTree, Element, parse, tostring
from datetime import datetime
import StringIO

from resource import Resource
from inventory import Inventory, InventoryDupeError
from mapper import Mapper, MapperError

SITEMAP_NS = 'http://www.sitemaps.org/schemas/sitemap/0.9'
RS_NS = 'http://www.openarchives.org/rs/terms/'
ATOM_NS = 'http://www.w3.org/2005/Atom'

class SitemapIndexError(Exception):
    """Exception on attempt to read a sitemapindex instead of sitemap"""

    def __init__(self, message=None, etree=None):
        self.message = message
        self.etree = etree

    def __repr__(self):
        return(self.message)

class SitemapIndex(Inventory):
    """Reuse an inventory to hold the set of sitemaps"""
    pass

class SitemapError(Exception):
    pass

class Sitemap(object):
    """Read and write sitemaps

    Implemented as a separate class that uses ResourceContainer (Inventory or
    ChangeSet) and Resource classes as data objects. Reads and write sitemaps, 
    including multiple file sitemaps.
    """

    def __init__(self, verbose=False, pretty_xml=False, allow_multifile=True, 
                 mapper=None):
        self.logger = logging.getLogger('sitemap')
        self.verbose=verbose
        self.pretty_xml=pretty_xml
        self.allow_multifile=allow_multifile
        self.mapper=mapper
        self.max_sitemap_entries=50000
        self.resources_class=Inventory
        self.resource_class=Resource
        # Information recorded for logging
        self.resources_created=None # Set during parsing sitemap
        self.sitemaps_created=None  # Set during parsing sitemapindex
        self.content_length=None    # Size of last sitemap read
        self.bytes_read=0           # Aggregate of content_length values

    ##### General sitemap methods that also handle sitemapindexes #####

    def write(self, resources=None, basename='/tmp/sitemap.xml'):
        """Write one or a set of sitemap files to disk

        resources is a ResourceContainer that may be an Inventory or
        a ChangeSet. This may be a generator so data is read as needed
        and length is determined at the end.

        basename is used as the name of the single sitemap file or the 
        sitemapindex for a set of sitemap files.

        Uses self.max_sitemap_entries to determine whether the inventory can 
        be written as one sitemap. If there are more entries and 
        self.allow_multifile is set true then 
        a set of sitemap files, with and index, will be written.
        """
        if (len(resources)>self.max_sitemap_entries):
            if (not self.allow_multifile):
                raise Exception("Too many entries for a single sitemap but multifile not enabled")
            # Work out how to name the sitemaps, attempt to add %05d before ".xml$", else append
            sitemap_prefix = basename
            sitemap_suffix = '.xml'
            if (basename[-4:] == '.xml'):
                sitemap_prefix = basename[:-4]
            # Use iterator over all resources and count off sets of
            # max_sitemap_entries to go into each sitemap, store the
            # names of the sitemaps as we go
            sitemaps={}
            resources_iter = iter(resources)
            for i in range(0,len(resources),self.max_sitemap_entries):
                file = sitemap_prefix + ( "%05d" % (len(sitemaps)) ) + sitemap_suffix
                if (self.verbose):
                    self.logger.info("Writing sitemap %s..." % (file))
                f = open(file, 'w')
                f.write(self.resources_as_xml(resources_iter,num_resources=self.max_sitemap_entries,include_capabilities=False))
                f.close()
                # Record timestamp
                sitemaps[file] = os.stat(file).st_mtime
            self.logger.info("Wrote %d sitemaps" % (len(sitemaps)))
            f = open(basename, 'w')
            if (self.verbose):
                self.logger.info("Writing sitemapindex %s..." % (basename))
            f.write(self.sitemapindex_as_xml(sitemaps=sitemaps,inventory=resources,include_capabilities=True))
            f.close()
            self.logger.info("Wrote sitemapindex %s" % (basename))
        else:
            f = open(basename, 'w')
            if (self.verbose):
                self.logger.info("Writing sitemap %s..." % (basename))
            f.write(self.resources_as_xml(resources))
            f.close()
            self.logger.info("Wrote sitemap %s" % (basename))

    def read(self, uri=None, resources=None):
        """Read sitemap from a URI including handling sitemapindexes

        Returns the inventory or changeset. If resources is not specified then
        it is assumed that an Inventory is to be read, pass in a ChangeSet object
        to read a changeset.

        Includes the subtlety that if the input URI is a local file and the 
        """
        if (resources is None):
            resources=Inventory()
        # 
        try:
            fh = URLopener().open(uri)
        except IOError as e:
            raise Exception("Failed to load sitemap/sitemapindex from %s (%s)" % (uri,str(e)))
        # Get the Content-Length if we can (works fine for local files)
        try:
            self.content_length = int(fh.info()['Content-Length'])
            self.bytes_read += self.content_length
        except KeyError:
            # If we don't get a length then c'est la vie
            pass
        self.logger.info( "Read sitemap/sitemapindex from %s" % (uri) )
        etree = parse(fh)
        # check root element: urlset (for sitemap), sitemapindex or bad
        self.sitemaps_created=0
        if (etree.getroot().tag == '{'+SITEMAP_NS+"}urlset"):
            self.logger.info( "Parsing as sitemap" )
            self.inventory_parse_xml(etree=etree, inventory=resources)
            self.sitemaps_created+=1
        elif (etree.getroot().tag == '{'+SITEMAP_NS+"}sitemapindex"):
            if (not self.allow_multifile):
                raise Exception("Got sitemapindex from %s but support for sitemapindex disabled" % (uri))
            self.logger.info( "Parsing as sitemapindex" )
            sitemaps=self.sitemapindex_parse_xml(etree=etree)
            sitemapindex_is_file = self.is_file_uri(uri)
            # now loop over all entries to read each sitemap and add to resources
            self.logger.info( "Now reading %d sitemaps" % len(sitemaps) )
            for sitemap_uri in sorted(sitemaps.resources.keys()):
                if (sitemapindex_is_file):
                    if (not self.is_file_uri(sitemap_uri)):
                        # Attempt to map URI to local file
                        remote_uri = sitemap_uri
                        sitemap_uri = self.mapper.src_to_dst(remote_uri)
                else:
                    # FIXME - need checks on sitemap_uri values:
                    # 1. should be in same server/path as sitemapindex URI
                    pass
                try:
                    fh = URLopener().open(sitemap_uri)
                except IOError as e:
                    raise Exception("Failed to load sitemap from %s listed in sitemap index %s (%s)" % (sitemap_uri,uri,str(e)))
                # Get the Content-Length if we can (works fine for local files)
                try:
                    self.content_length = int(fh.info()['Content-Length'])
                    self.bytes_read += self.content_length
                except KeyError:
                    # If we don't get a length then c'est la vie
                    pass
                self.logger.info( "Read sitemap from %s (%d)" % (sitemap_uri,self.content_length) )
                self.inventory_parse_xml( fh=fh, inventory=resources )
                self.sitemaps_created+=1
        else:
            raise ValueError("XML read from %s is not a sitemap or sitemapindex" % (sitemap_uri))
        return(resources)

    ##### Resource methods #####

    def resource_etree_element(self, resource, element_name='url'):
        """Return xml.etree.ElementTree.Element representing the resource

        Returns and element for the specified resource, of the form <url> 
        with enclosed properties that are based on the sitemap with extensions
        for ResourceSync.
        """
        e = Element(element_name)
        sub = Element('loc')
        sub.text=resource.uri
        e.append(sub)
        if (resource.timestamp is not None):
            sub = Element('lastmod')
            sub.text = str(resource.lastmod) #W3C Datetime in UTC
            e.append(sub)
        if (resource.size is not None):
            sub = Element('rs:size')
            sub.text = str(resource.size)
            e.append(sub)
        if (resource.md5 is not None):
            sub = Element('rs:md5')
            sub.text = str(resource.md5)
            e.append(sub)
        # FIXME - should consider subclassing Sitemap for Changesets
        if (hasattr(resource,'changeid') and resource.changeid is not None):
            sub = Element('rs:changeid')
            sub.text = str(resource.changeid)
            e.append(sub)
        if (hasattr(resource,'changetype') and resource.changetype is not None):
            sub = Element('rs:changetype')
            sub.text = str(resource.changetype)
            e.append(sub)
        if (self.pretty_xml):
            e.tail="\n"
        return(e)

    def resource_as_xml(self,resource,indent=' '):
        """Return string for the the resource as part of an XML sitemap

        """
        e = self.resource_etree_element(resource)
        if (sys.version_info < (2,7)):
            #must not specify method='xml' in python2.6
            return(tostring(e, encoding='UTF-8'))
        else:
            return(tostring(e, encoding='UTF-8', method='xml'))

    def resource_from_etree(self, etree):
        """Construct a Resource from an etree

        The parsing is properly namespace aware but we search just for 
        the elements wanted and leave everything else alone. Provided 
        there is a <loc> element then we'll go ahead and extract as much 
        as possible.
        """
        loc = etree.findtext('{'+SITEMAP_NS+"}loc")
        if (loc is None):
            raise SitemapError("Missing <loc> element while parsing <url> in sitemap")
        # We at least have a URI, make this object
        resource=self.resource_class(uri=loc)
        # and then proceed to look for other resource attributes
        lastmod = etree.findtext('{'+SITEMAP_NS+"}lastmod")
        if (lastmod is not None):
            resource.lastmod=lastmod
        size = etree.findtext('{'+RS_NS+"}size")
        if (size is not None):
            resource.size=int(size) #FIXME should throw exception if not number
        md5 = etree.findtext('{'+RS_NS+"}md5")
        if (md5 is not None):
            resource.md5=md5
        # Ignore the changeid and changetype elements unless resource has 
        # these attributes. This gives the flexibility to read a changeset 
        # as a plain inventory if desired
        if (hasattr(resource, 'changeid')):
            changeid = etree.findtext('{'+RS_NS+"}changeid")
            if (changeid is not None):
                resource.changeid=changeid
        if (hasattr(resource, 'changetype')):
            changetype = etree.findtext('{'+RS_NS+"}changetype")
            if (changetype is not None):
                resource.changetype=changetype
        return(resource)

    ##### ResourceContainer (Inventory or ChangeSet) methods #####

    def resources_as_xml(self, resources, num_resources=None, include_capabilities=True):
        """Return XML for a set of resources in sitemap format
        
        resources is either an iterable or iterator of Resource objects.

        If num_resources is not None then only that number will be written
        before exiting.
        """
        # will include capabilities if allowed and if there are some
        include_capabilities = include_capabilities and (len(resources.capabilities)>0)
        namespaces = { 'xmlns': SITEMAP_NS, 'xmlns:rs': RS_NS }
        if (include_capabilities):
            namespaces['xmlns:atom'] = ATOM_NS
        root = Element('urlset', namespaces)
        if (self.pretty_xml):
            root.text="\n"
        if (include_capabilities):
            self.add_capabilities_to_etree(root,resources.capabilities)
        # now add the entries from either an iterable or an iterator
        for r in resources:
            e=self.resource_etree_element(r)
            root.append(e)
            if (num_resources is not None):
                num_resources-=1
                if (num_resources==0):
                    break
        # have tree, now serialize
        tree = ElementTree(root);
        xml_buf=StringIO.StringIO()
        if (sys.version_info < (2,7)):
            tree.write(xml_buf,encoding='UTF-8')
        else:
            tree.write(xml_buf,encoding='UTF-8',xml_declaration=True,method='xml')
        return(xml_buf.getvalue())

    def inventory_parse_xml(self, fh=None, etree=None, inventory=None):
        """Parse XML Sitemap from fh or etree and add resources to an inventory object

        Returns the inventory.

        Also sets self.resources_created to be the number of resources created. 
        We adopt a very lax approach here. The parsing is properly namespace 
        aware but we search just for the elements wanted and leave everything 
        else alone.

        The one exception is detection of Sitemap indexes. If the root element
        indicates a sitemapindex then an SitemapIndexError() is thrown 
        and the etree passed along with it.
        """
        if (inventory is None):
            inventory=self.resources_class()
        if (fh is not None):
            etree=parse(fh)
        elif (etree is None):
            raise ValueError("Neither fh or etree set")
        # check root element: urlset (for sitemap), sitemapindex or bad
        if (etree.getroot().tag == '{'+SITEMAP_NS+"}urlset"):
            self.resources_created=0
            for url_element in etree.findall('{'+SITEMAP_NS+"}url"):
                r = self.resource_from_etree(url_element)
                try:
                    inventory.add( r )
                except InventoryDupeError:
                    self.logger.warning("dupe: %s (%s =? %s)" % 
                        (r.uri,r.lastmod,inventory.resources[r.uri].lastmod))
                self.resources_created+=1
            return(inventory)
        elif (etree.getroot().tag == '{'+SITEMAP_NS+"}sitemapindex"):
            raise SitemapIndexError("Got sitemapindex when expecting sitemap",etree)
        else:
            raise ValueError("XML is not sitemap or sitemapindex")

    ##### Sitemap Index #####

    def sitemapindex_as_xml(self, file=None, sitemaps={}, inventory=None, include_capabilities=False ):
        """Return a sitemapindex as an XML string

        Format:
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <sitemap>
            <loc>http://www.example.com/sitemap1.xml.gz</loc>
            <lastmod>2004-10-01T18:23:17+00:00</lastmod>
          </sitemap>
          ...more...
        </sitemapeindex>
        """
        include_capabilities = include_capabilities and (len(inventory.capabilities)>0)
        namespaces = { 'xmlns': SITEMAP_NS }
        if (include_capabilities):
            namespaces['xmlns:atom'] = ATOM_NS
        root = Element('sitemapindex', namespaces)
        if (self.pretty_xml):
            root.text="\n"
        if (include_capabilities):
            self.add_capabilities_to_etree(root,inventory.capabilities)
        for file in sitemaps.keys():
            try:
                uri = self.mapper.dst_to_src(file)
            except MapperError:
                uri = 'file://'+file
                if (self.verbose):
                    self.logger.error("sitemapindex: can't map %s into URI space, writing %s" % (file,uri))
            # Make a Resource for the Sitemap and serialize
            smr = Resource( uri=uri, timestamp=sitemaps[file] )
            root.append( self.resource_etree_element(smr, element_name='sitemap') )
        tree = ElementTree(root);
        xml_buf=StringIO.StringIO()
        if (sys.version_info < (2,7)):
            tree.write(xml_buf,encoding='UTF-8')
        else:
            tree.write(xml_buf,encoding='UTF-8',xml_declaration=True,method='xml')
        return(xml_buf.getvalue())

    def sitemapindex_parse_xml(self, fh=None, etree=None, sitemapindex=None):
        """Parse XML SitemapIndex from fh and return sitemap info

        Returns the SitemapIndex object.

        Also sets self.sitemaps_created to be the number of resources created. 
        We adopt a very lax approach here. The parsing is properly namespace 
        aware but we search just for the elements wanted and leave everything 
        else alone.

        The one exception is detection of a Sitemap when an index is expected. 
        If the root element indicates a sitemap then a SitemapIndexError() is 
        thrown and the etree passed along with it.
        """
        if (sitemapindex is None):
            sitemapindex=SitemapIndex()
        if (fh is not None):
            etree=parse(fh)
        elif (etree is None):
            raise ValueError("Neither fh or etree set")
        # check root element: urlset (for sitemap), sitemapindex or bad
        if (etree.getroot().tag == '{'+SITEMAP_NS+"}sitemapindex"):
            self.sitemaps_created=0
            for sitemap_element in etree.findall('{'+SITEMAP_NS+"}sitemap"):
                # We can parse the inside just like a <url> element indicating a resource
                sitemapindex.add( self.resource_from_etree(sitemap_element) )
                self.sitemaps_created+=1
            return(sitemapindex)
        elif (etree.getroot().tag == '{'+SITEMAP_NS+"}urlset"):
            raise SitemapIndexError("Got sitemap when expecting sitemapindex",etree)
        else:
            raise ValueError("XML is not sitemap or sitemapindex")


    ##### Capabilities #####

    def add_capabilities_to_etree(self, etree, capabilities):
        """ Add capabilities to the etree supplied

        Each capability is written out as on atom:link element where the
        attributes are represented as a dictionary.
        """
        for c in sorted(capabilities.keys()):
            # make attributes by space concatenating any capability dict values 
            # that are arrays
            atts = { 'href': c }
            for a in capabilities[c]:
                value=capabilities[c][a]
                if (a == 'attributes'):
                    a='rel'
                if (isinstance(value, str)):
                    atts[a]=value
                else:
                    atts[a]=' '.join(value)
            e = Element('atom:link', atts)
            if (self.pretty_xml):
                e.tail="\n"
            etree.append(e)

    ##### Utility #####

    def is_file_uri(self, uri):
        """Return true is uri looks like a local file URI, false otherwise"""
        return(re.match('file:',uri) or re.match('/',uri))
