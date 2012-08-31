"""ResourceSync client implementation"""

import sys
import urllib
import os.path
import datetime
import distutils.dir_util 
import re
import time

from resync.inventory_builder import InventoryBuilder
from resync.inventory import Inventory
from resync.changeset import ChangeSet
from resync.mapper import Mapper
from resync.sitemap import Sitemap
from resync.dump import Dump
from resync.resource_change import ResourceChange
from resync.url_authority import UrlAuthority

class ClientFatalError(Exception):
    """Non-recoverable error in client, should include message to user"""
    pass

class Client(object):
    """Implementation of a ResourceSync client"""

    def __init__(self, checksum=False, verbose=False, dryrun=False, logger=None):
        super(Client, self).__init__()
        self.checksum = checksum
        self.verbose = verbose
        self.dryrun = dryrun
        self.logger = logger
        self.mapper = None
        self.sitemap_name = 'sitemap.xml'
        self.dump_format = None
        self.exclude_patterns = []
        self.allow_multifile = True
        self.noauth = False
        self.max_sitemap_entries = None

    @property
    def mappings(self):
        """Provide access to mappings list within Mapper object"""
        if (self.mapper is None):
            raise ClientFatalError("No mappings specified")
        return(self.mapper.mappings)

#    @mappings.setter
    def set_mappings(self,mappings):
        """Build and set Mapper object based on input mappings"""
        self.mapper = Mapper(mappings)

    @property
    def sitemap(self):
        """Return the sitemap URI base on maps or explicit settings"""
        if (re.match(r"\w+:",self.sitemap_name)):
            # looks like URI
            return(self.sitemap_name)
        elif (re.match(r"/",self.sitemap_name)):
            # looks like full path
            return(self.sitemap_name)
        else:
            # build from mapping with name appended
            return(self.mappings[0].src_uri + '/' + self.sitemap_name)

    @property
    def inventory(self):
        """Return inventory on disk based on current mappings

        Return inventory. Uses existing self.mapper settings.
        """
        ### 0. Sanity checks
        if (len(self.mappings)<1):
            raise ClientFatalError("No source to destination mapping specified")
        ### 1. Build from disk
        ib = InventoryBuilder(do_md5=self.checksum,verbose=self.verbose,mapper=self.mapper)
        ib.add_exclude_files(self.exclude_patterns)
        return( ib.from_disk() )

    def sync_or_audit(self, allow_deletion=False, audit_only=False):
        ### 0. Sanity checks
        if (len(self.mappings)<1):
            raise ClientFatalError("No source to destination mapping specified")
        ### 1. Get inventories from both src and dst 
        # 1.a source inventory
        ib = InventoryBuilder(verbose=self.verbose,mapper=self.mapper)
        try:
            if (self.verbose):
                print "Reading sitemap %s ..." % (self.sitemap)
            self.logger.info( repr(ResourceChange(uri=self.sitemap,changetype="START_GET_SITEMAP")) )
            src_sitemap = Sitemap(verbose=self.verbose, allow_multifile=self.allow_multifile, mapper=self.mapper)
            src_inventory = src_sitemap.read(uri=self.sitemap)
            self.logger.info( repr(ResourceChange(uri=self.sitemap,size=src_sitemap.bytes_read,changetype="END_GET_SITEMAP")) )
        except Exception as e:
            raise ClientFatalError("Can't read source inventory from %s (%s)" % (self.sitemap,str(e)))
        if (self.verbose):
            print "Read source inventory, %d resources listed" % (len(src_inventory))
        if (len(src_inventory)==0):
            raise ClientFatalError("Aborting as there are no resources to sync")
        if (self.checksum and not src_inventory.has_md5()):
            self.checksum=False
            print "Not calculating checksums on destination as not present in source inventory"
        # 1.b destination inventory mapped back to source URIs
        ib.do_md5=self.checksum
        dst_inventory = ib.from_disk()
        ### 2. Compare these inventorys respecting any comparison options
        (same,updated,deleted,created)=dst_inventory.compare(src_inventory)   
        ### 3. Report status and planned actions
        status = "  IN SYNC  "
        if (len(updated)>0 or len(deleted)>0 or len(created)>0):
            status = "NOT IN SYNC"
        print "Status: %s (same=%d, updated=%d, deleted=%d, created=%d)" %\
              (status,len(same),len(updated),len(deleted),len(created))
        if (audit_only):
            return
        ### 4. Check that sitemap has authority over URIs listed
        uauth = UrlAuthority(self.sitemap)
        for resource in src_inventory:
            if (not uauth.has_authority_over(resource.uri)):
                if (self.noauth):
                    self.logger.warning("Sitemap (%s) mentions resource at a location it does not have authority over (%s)" % (self.sitemap,resource.uri))
                else:
                    raise ClientFatalError("Aborting as sitemap (%s) mentions resource at a location it does not have authority over (%s), override with --noauth" % (self.sitemap,resource.uri))
        ### 5. Grab files to do sync
        for resource in updated:
            uri = resource.uri
            file = self.mapper.src_to_dst(uri)
            if (self.verbose):
                print "updated: %s -> %s" % (uri,file)
            self.update_resource(resource,file,'UPDATED')
        for resource in created:
            uri = resource.uri
            file = self.mapper.src_to_dst(uri)
            if (self.verbose):
                print "created: %s -> %s" % (uri,file)
            self.update_resource(resource,file,'CREATED')
        for resource in deleted:
            uri = resource.uri
            if (allow_deletion):
                file = self.mapper.src_to_dst(uri)
                if (self.dryrun):
                    print "dryrun: would delete %s -> %s" % (uri,file)
                else:
                    os.unlink(file)
                    if (self.verbose):
                        print "deleted: %s -> %s" % (uri,file)
                    self.logger.info( repr(ResourceChange(resource=resource, changetype="DELETED")) )
            else:
                if (self.verbose):
                    print "nodelete: would delete %s (--delete to enable)" % uri

    def update_resource(self, resource, file, changetype=None):
        """Update resource from uri to file on local system

        Update means two things:
        1. GET resources
        2. set mtime in local time to be equal to timestamp in UTC (should perhaps
        or at least warn if different from LastModified from the GET response instead 
        but maybe warn if different (or just earlier than) the lastmod we expected 
        from the inventory
        """
        path = os.path.dirname(file)
        distutils.dir_util.mkpath(path)
        if (self.dryrun):
            print "dryrun: would GET %s --> %s" % (resource.uri,file)
        else:
            urllib.urlretrieve(resource.uri,file)
            self.logger.info( repr(ResourceChange(resource=resource, changetype=changetype)) )
            if (resource.timestamp is not None):
                unixtime = int(resource.timestamp) #no fractional
                os.utime(file,(unixtime,unixtime))
            

    def parse_sitemap(self):
        s=Sitemap(verbose=self.verbose, allow_multifile=self.allow_multifile)
        if (self.verbose):
            print "Reading sitemap(s) from %s ..." % (sitemap)
        i = s.read(sitemap)
        num_entries = len(i)
        print "Read sitemap with %d entries in %d sitemaps" % (num_entries,s.sitemaps_created)
        if (self.verbose):
            to_show = 100
            override_str = ' (override with --max-sitemap-entries)'
            if (self.max_sitemap_entries):
                to_show = self.max_sitemap_entries
                override_str = ''
            if (num_entries>to_show):
                print "Showing first %d entries sorted by URI%s..." % (to_show,override_str)
            n=0
            for r in i:
                print r
                n+=1
                if ( n >= to_show ):
                    break

    def write_sitemap(self,outfile=None,capabilities=None,dump=None):
        # Set up base_path->base_uri mappings, get inventory from disk
        i = self.inventory
        i.capabilities = capabilities
        s=Sitemap(verbose=self.verbose, pretty_xml=True, allow_multifile=self.allow_multifile,
	          mapper=self.mapper)
        if (self.max_sitemap_entries is not None):
            s.max_sitemap_entries = self.max_sitemap_entries
        if (outfile is None):
            print s.resources_as_xml(i)
        else:
            s.write(i,basename=outfile)
        self.write_dump_if_requested(i,dump)

    def changeset_sitemap(self,outfile=None,ref_sitemap=None,newref_sitemap=None,
                          capabilities=None,dump=None):
        # 1. Get and parse reference sitemap
        old_inv = self.read_reference_sitemap(ref_sitemap)
        # 2. Depending on whether a newref_sitemap was specified, either read that 
        # or build inventory from files on disk
        if (newref_sitemap is None):
            # Get inventory from disk
            new_inv = self.inventory
        else:
            new_inv = self.read_reference_sitemap(newref_sitemap,name='new reference')
        # 3. Calculate changeset
        (same,updated,deleted,created)=old_inv.compare(new_inv)   
        changeset = ChangeSet()
        changeset.capabilities = capabilities
        changeset.add_changed_resources( updated, changetype='UPDATED' )
        changeset.add_changed_resources( deleted, changetype='DELETED' )
        changeset.add_changed_resources( created, changetype='CREATED' )
        # 4. Write out changeset
        s = Sitemap(verbose=self.verbose, pretty_xml=True, allow_multifile=self.allow_multifile,
	            mapper=self.mapper)
        if (self.max_sitemap_entries is not None):
            s.max_sitemap_entries = self.max_sitemap_entries
        if (outfile is None):
            print s.resources_as_xml(changeset)
        else:
            s.write(changeset,basename=outfile)
        self.write_dump_if_requested(changeset,dump)

    def write_dump_if_requested(self,inventory,dump):
        if (dump is None):
            return
        if (self.verbose):
            print "Writing dump to %s..." % (dump)
        d = Dump(format=self.dump_format)
        d.write(inventory=inventory,dumpfile=dump)

    def read_reference_sitemap(self,ref_sitemap,name='reference'):
        """Read reference sitemap and return the inventory

        name parameter just uses in output messages to say what type
        of sitemap is being read.
        """
        sitemap = Sitemap(verbose=self.verbose, allow_multifile=self.allow_multifile, 
                     mapper=self.mapper)
        if (self.verbose):
            print "Reading %s sitemap(s) from %s ..." % (name,ref_sitemap)
        i = sitemap.read(ref_sitemap)
        num_entries = len(i)
        print "Read %s sitemap with %d entries in %d sitemaps" % (name,num_entries,sitemap.sitemaps_created)
        if (self.verbose):
            to_show = 100
            override_str = ' (override with --max-sitemap-entries)'
            if (self.max_sitemap_entries):
                to_show = self.max_sitemap_entries
                override_str = ''
            if (num_entries>to_show):
                print "Showing first %d entries sorted by URI%s..." % (to_show,override_str)
            n=0
            for r in i:
                print r
                n+=1
                if ( n >= to_show ):
                    break
        return(i)

if __name__ == '__main__':
    main()
