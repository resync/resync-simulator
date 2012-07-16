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
from resync.mapper import Mapper
from resync.sitemap import Sitemap
from resync.dump import Dump

class ClientFatalError(Exception):
    """Non-recoverable error in client, should include message to user"""
    pass

class Client():
    """Implementation of a ResourceSync client"""

    def __init__(self, checksum=False, verbose=False, dryrun=False):
        self.checksum = checksum
        self.verbose = verbose
        self.dryrun = dryrun
        self.mapper = None
        self.sitemap_name = 'sitemap.xml'
        self.dump_format = None
        self.allow_multifile = False
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
            src_inventory = ib.get(self.sitemap)
        except IOError as e:
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
        (num_same,updated,deleted,created)=dst_inventory.compare(src_inventory)   
        ### 3. Report status and planned actions
        status = "  IN SYNC  "
        if (len(updated)>0 or len(deleted)>0 or len(created)>0):
            status = "NOT IN SYNC"
        print "Status: %s (same=%d, updated=%d, deleted=%d, created=%d)" %\
              (status,num_same,len(updated),len(deleted),len(created))

        if (audit_only):
            return
        ### 4. Grab files to do sync
        for uri in updated:
            file = self.mapper.src_to_dst(uri)
            if (self.verbose):
                print "updated: %s -> %s" % (uri,file)
            self.update_resource(uri,file,src_inventory.resources[uri].timestamp)
        for uri in created:
            file = self.mapper.src_to_dst(uri)
            self.update_resource(uri,file,src_inventory.resources[uri].timestamp)
        for uri in deleted:
            if (allow_deletion):
                file = self.mapper.src_to_dst(uri)
                if (self.dryrun):
                    print "dryrun: would delete %s -> %s" % (uri,file)
                else:
                    os.unlink(file)
                    if (self.verbose):
                        print "deleted: %s -> %s" % (uri,file)
            else:
                if (self.verbose):
                    print "nodelete: would delete %s (--delete to enable)" % uri

    def update_resource(self, uri, file, timestamp=None):
        """Update resource from uri to file on local system

        Update means two things:
        1. GET resources
        2. set mtime to be equal to timestamp (should probably use LastModified 
        from the GET response instead but maybe warn if different (or just 
        earlier than) the lastmod we expected from the inventory
        """
        path = os.path.dirname(file)
        distutils.dir_util.mkpath(path)
        if (self.dryrun):
            print "dryrun: would GET %s --> %s" % (uri,file)
        else:
            urllib.urlretrieve(uri,file)
            if (self.verbose):
                print "created: %s -> %s" % (uri,file)
            if (timestamp is not None):
                unixtime=int(timestamp) #get rid of any fractional seconds
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
            for r in i.resource_uris():
                print i.resources[r]
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
            print s.inventory_as_xml(i)
        else:
            s.write(i,basename=outfile)
        self.write_dump_if_requested(i,dump)

    def changeset_sitemap(self,outfile=None,ref_sitemap=None,capabilities=None,
                          dump=None):
        # 1. Get and parse reference sitemap
        rs = Sitemap(verbose=self.verbose, allow_multifile=self.allow_multifile, 
                     mapper=self.mapper)
        if (self.verbose):
            print "Reading sitemap(s) from %s ..." % (ref_sitemap)
        ri = rs.read(ref_sitemap)
        num_entries = len(ri)
        print "Read reference sitemap with %d entries in %d sitemaps" % (num_entries,rs.sitemaps_created)
        if (self.verbose):
            to_show = 100
            override_str = ' (override with --max-sitemap-entries)'
            if (self.max_sitemap_entries):
                to_show = self.max_sitemap_entries
                override_str = ''
            if (num_entries>to_show):
                print "Showing first %d entries sorted by URI%s..." % (to_show,override_str)
            n=0
            for r in ri.resource_uris():
                print ri.resources[r]
                n+=1
                if ( n >= to_show ):
                    break
        # 2. Set up base_path->base_uri mappings, get inventory from disk
        disk_inventory = self.inventory
        # 3. Calculate changeset
        (num_same,updated,deleted,created)=ri.compare(disk_inventory)   
        changeset = Inventory()
        changeset.capabilities = capabilities
        changeset.add( disk_inventory.changeset( updated, changetype='updated' ) )
        changeset.add( ri.changeset( deleted, changetype='deleted' ) )
        changeset.add( disk_inventory.changeset( created, changetype='created' ) )
        # 4. Write out changeset
        s = Sitemap(verbose=self.verbose, pretty_xml=True, allow_multifile=self.allow_multifile,
	            mapper=self.mapper)
        if (self.max_sitemap_entries is not None):
            s.max_sitemap_entries = self.max_sitemap_entries
        if (outfile is None):
            print s.inventory_as_xml(changeset)
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

if __name__ == '__main__':
    main()
