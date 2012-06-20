"""ResourceSync client implementation"""

import sys
import urllib
import os.path
import distutils.dir_util 
import time
import datetime

from resync.inventory_builder import InventoryBuilder
from resync.inventory import Inventory
from resync.mapper import Mapper

class ClientFatalError(Exception):
    """Non-recoverable error in client, should include message to user"""
    pass

class Client():
    """Implementation of a ResourceSync client"""

    def __init__(self, checksum=False, verbose=False):
        self.checksum = checksum
        self.verbose = verbose
        self.mappings = {}

    def set_mappings(self, mappings=None):
        """Set up or add to the path=uri mappings for this client

        Format of each mapping is path=uri
        """
        for mapping in mappings:
            l=mapping.split('=')
            if (len(l)!=2):
                raise ClientFatalError("Bad mapping argument (%s), got %s"%(mapping,str(l)))
            (base_path,base_uri)=l
            if (base_path in self.mappings):
                raise ClientFatalError("Attempt to set duplicate mapping for path %s with %s" % (base_path, mapping))
            self.mappings[base_path] = base_uri


    @property
    def inventory(self):
        """Return inventory on disk based on current mappings

        Return inventory. Uses existing self.mappings settings.
        """
        ib = InventoryBuilder(do_md5=self.checksum)
        m = Inventory()
        for base_path in sorted(self.mappings.keys()):
            base_uri = self.mappings[base_path]
            m=ib.from_disk(base_path,base_uri,inventory=m)
        return m

    def sync_or_audit(self, src_uri, dst_path, allow_deletion=False, 
                      audit_only=False):
        ### 1. Get inventorys from both src and dst 
        # 1.a source inventory
        ib = InventoryBuilder()
        try:
            src_inventory = ib.get(src_uri)
        except IOError as e:
            raise ClientFatalError("Can't read source inventory (%s)" % str(e))
        if (self.verbose):
            print "Read src inventory from %s, %d resources listed" % (src_uri,len(src_inventory))
        if (len(src_inventory)==0):
            raise ClientFatalError("Aborting as there are no resources to sync")
        if (self.checksum and not src_inventory.has_md5()):
            self.checksum=False
            print "Not calculating checksums on destination as not present in source inventory"
        # 1.b destination inventory mapped back to source URIs
        segments = src_uri.split('/')
        segments.pop()
        url_prefix='/'.join(segments)
        ib.do_md5=self.checksum
        dst_inventory = ib.from_disk(dst_path,url_prefix)
        ### 2. Compare these inventorys respecting any comparison options
        (num_same,changed,deleted,added)=dst_inventory.compare(src_inventory)   
        ### 3. Report status and planned actions
        status = "  IN SYNC  "
        if (len(changed)>0 or len(deleted)>0 or len(added)>0):
            status = "NOT IN SYNC"
        print "Status: %s (same=%d, changed=%d, deleted=%d, added=%d)" %\
              (status,num_same,len(changed),len(deleted),len(added))

        if (audit_only):
            return
        ### 4. Grab files to do sync
        mapper = Mapper( [ url_prefix+'='+dst_path ] )
        for uri in changed:
            file = mapper.src_to_dst(uri)
            if (self.verbose):
                print "changed: %s -> %s" % (uri,file)
            self.update_resource(uri,file,src_inventory.resources[uri].timestamp)
        for uri in added:
            file = mapper.src_to_dst(uri)
            if (self.verbose):
                print "added: %s -> %s" % (uri,file)
            self.update_resource(uri,file,src_inventory.resources[uri].timestamp)
        for uri in deleted:
            if (allow_deletion):
                file = mapper.src_to_dst(uri)
                if (self.verbose):
                    print "deleted: %s -> %s" % (uri,file)
                os.unlink(file)
            else:
                if (self.verbose):
                    print "would delete %s (--delete to enable)" % uri

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
        urllib.urlretrieve(uri,file)
        if (timestamp is not None):
            unixtime=int(timestamp) #get rid of any fractional seconds
            os.utime(file,(unixtime,unixtime))
