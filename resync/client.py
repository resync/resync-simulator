"""ResourceSync client implementation"""

import sys
import urllib
import os.path
import datetime
import distutils.dir_util 
import re
import time
import logging

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
    """Implementation of a ResourceSync client

    Logging is used for both console output and for detailed logs for
    automated analysis. Levels used:
      warning - usually shown to user
      info    - verbose output
      debug   - very verbose for automated analysis
    """

    def __init__(self, checksum=False, verbose=False, dryrun=False):
        super(Client, self).__init__()
        self.checksum = checksum
        self.verbose = verbose
        self.dryrun = dryrun
        self.logger = logging.getLogger('client')
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

    def set_mappings(self,mappings):
        """Build and set Mapper object based on input mappings"""
        self.mapper = Mapper(mappings)

    def sitemap_changeset_uri(self,basename):
        """Get full URI (filepath) for sitemap/changeset based on basename"""
        if (re.match(r"\w+:",basename)):
            # looks like URI
            return(basename)
        elif (re.match(r"/",basename)):
            # looks like full path
            return(basename)
        else:
            # build from mapping with name appended
            return(self.mappings[0].src_uri + '/' + basename)

    @property
    def sitemap(self):
        """Return the sitemap URI based on maps or explicit settings"""
        return(self.sitemap_changeset_uri(self.sitemap_name))

    @property
    def inventory(self):
        """Return inventory on disk based on current mappings

        Return inventory. Uses existing self.mapper settings.
        """
        ### 0. Sanity checks
        if (len(self.mappings)<1):
            raise ClientFatalError("No source to destination mapping specified")
        ### 1. Build from disk
        ib = InventoryBuilder(do_md5=self.checksum,mapper=self.mapper)
        ib.add_exclude_files(self.exclude_patterns)
        return( ib.from_disk() )

    def log_event(self, change):
        """Log a ResourceChange object as an event for automated analysis"""
        self.logger.debug( "Event: "+repr(change) )

    def sync_or_audit(self, allow_deletion=False, audit_only=False):
        action = ( 'audit' if (audit_only) else 'sync' ) 
        self.logger.debug("Starting "+action)
        ### 0. Sanity checks
        if (len(self.mappings)<1):
            raise ClientFatalError("No source to destination mapping specified")
        ### 1. Get inventories from both src and dst 
        # 1.a source inventory
        ib = InventoryBuilder(mapper=self.mapper)
        try:
            self.logger.info("Reading sitemap %s" % (self.sitemap))
            src_sitemap = Sitemap(allow_multifile=self.allow_multifile, mapper=self.mapper)
            src_inventory = src_sitemap.read(uri=self.sitemap)
            self.logger.debug("Finished reading sitemap")
        except Exception as e:
            raise ClientFatalError("Can't read source inventory from %s (%s)" % (self.sitemap,str(e)))
        self.logger.info("Read source inventory, %d resources listed" % (len(src_inventory)))
        if (len(src_inventory)==0):
            raise ClientFatalError("Aborting as there are no resources to sync")
        if (self.checksum and not src_inventory.has_md5()):
            self.checksum=False
            self.logger.info("Not calculating checksums on destination as not present in source inventory")
        # 1.b destination inventory mapped back to source URIs
        ib.do_md5=self.checksum
        dst_inventory = ib.from_disk()
        ### 2. Compare these inventorys respecting any comparison options
        (same,updated,deleted,created)=dst_inventory.compare(src_inventory)   
        ### 3. Report status and planned actions
        status = "  IN SYNC  "
        if (len(updated)>0 or len(deleted)>0 or len(created)>0):
            status = "NOT IN SYNC"
        self.logger.warning("Status: %s (same=%d, updated=%d, deleted=%d, created=%d)" %\
              (status,len(same),len(updated),len(deleted),len(created)))
        if (audit_only):
            self.logger.debug("Completed "+action)
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
            self.logger.info("updated: %s -> %s" % (uri,file))
            self.update_resource(resource,file,'UPDATED')
        for resource in created:
            uri = resource.uri
            file = self.mapper.src_to_dst(uri)
            self.logger.info("created: %s -> %s" % (uri,file))
            self.update_resource(resource,file,'CREATED')
        for resource in deleted:
            uri = resource.uri
            if (allow_deletion):
                file = self.mapper.src_to_dst(uri)
                if (self.dryrun):
                    self.logger.info("dryrun: would delete %s -> %s" % (uri,file))
                else:
                    os.unlink(file)
                    self.logger.info("deleted: %s -> %s" % (uri,file))
                    self.log_event(ResourceChange(resource=resource, changetype="DELETED"))
            else:
                self.logger.info("nodelete: would delete %s (--delete to enable)" % uri)
        self.logger.debug("Completed "+action)

    def incremental(self, allow_deletion=False, changeset_uri=None):
        self.logger.debug("Starting incremental sync")
        ### 0. Sanity checks
        if (len(self.mappings)<1):
            raise ClientFatalError("No source to destination mapping specified")
        ### 1. Get URI of changeset, from sitemap or explicit
        if (changeset_uri):
            # Translate as necessary using maps
            changeset = self.sitemap_changeset_uri(changeset_uri)
        else:
            # Get sitemap
            try:
                self.logger.info("Reading sitemap %s" % (self.sitemap))
                #FIXME - don't want to read sitemaps ref'd by sitemap index... need flag to disable
                src_sitemap = Sitemap(allow_multifile=self.allow_multifile, mapper=self.mapper)
                src_inventory = src_sitemap.read(uri=self.sitemap)
                self.logger.debug("Finished reading sitemap")
            except Exception as e:
                raise ClientFatalError("Can't read source sitemap from %s (%s)" % (self.sitemap,str(e)))
            # Extract changeset location
            # FIXME - need to completely rework the way we handle/store capabilities
            changeset = None
            for cap in src_inventory.capabilities.keys():
                t = src_inventory.capabilities[cap].get('type')
                if (t is not None and t=='changeset'):
                    changeset=cap
            if (changeset is None):
                raise ClientFatalError("Failed to extract changeset location from sitemap %s" % (self.sitemap))
            time.sleep(2) # FIXME - https://github.com/resync/simulator/issues/25
        ### 2. Read changeset from source
        ib = InventoryBuilder(mapper=self.mapper)
        try:
            self.logger.info("Reading changeset %s" % (changeset))
            src_sitemap = Sitemap(allow_multifile=self.allow_multifile, mapper=self.mapper)
            src_changeset = src_sitemap.read(uri=changeset, changeset=True)
            self.logger.debug("Finished reading changeset")
        except Exception as e:
            raise ClientFatalError("Can't read source changeset from %s (%s)" % (changeset,str(e)))
        self.logger.info("Read source changeset, %d resources listed" % (len(src_changeset)))
        if (len(src_changeset)==0):
            raise ClientFatalError("Aborting as there are no resources to sync")
        if (self.checksum and not src_changeset.has_md5()):
            self.checksum=False
            self.logger.info("Not calculating checksums on destination as not present in source inventory")
        ### 3. Check that sitemap has authority over URIs listed
        # FIXME - What does authority mean for changeset? Here use both the
        # changeset URI and, if we used it, the sitemap URI
        uauth_cs = UrlAuthority(changeset)
        if (not changeset_uri):
            uauth_sm = UrlAuthority(self.sitemap)
        for resource in src_changeset:
            if (not uauth_cs.has_authority_over(resource.uri) and 
                (changeset_uri or not uauth_sm.has_authority_over(resource.uri))):
                if (self.noauth):
                    self.logger.warning("Changeset (%s) mentions resource at a location it does not have authority over (%s)" % (changeset,resource.uri))
                else:
                    raise ClientFatalError("Aborting as changeset (%s) mentions resource at a location it does not have authority over (%s), override with --noauth" % (changeset,resource.uri))
        ### 3. Apply changes
        for resource in src_changeset:
            uri = resource.uri
            file = self.mapper.src_to_dst(uri)
            if (resource.changetype == 'UPDATED'):
                self.logger.info("updated: %s -> %s" % (uri,file))
                self.update_resource(resource,file,'UPDATED')
            elif (resource.changetype == 'CREATED'):
                self.logger.info("created: %s -> %s" % (uri,file))
                self.update_resource(resource,file,'CREATED')
            elif (resource.changetype == 'DELETED'):
                if (allow_deletion):
                    file = self.mapper.src_to_dst(uri)
                    if (self.dryrun):
                        self.logger.info("dryrun: would delete %s -> %s" % (uri,file))
                    else:
                        os.unlink(file)
                        self.logger.info("deleted: %s -> %s" % (uri,file))
                        self.log_event(ResourceChange(resource=resource, changetype="DELETED"))
                else:
                    self.logger.info("nodelete: would delete %s (--delete to enable)" % uri)
            else:
                raise ClientError("Unknown change type %s" % (resource.changetype) )
        self.logger.debug("Completed incremental stuff")

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
            self.logger.info("dryrun: would GET %s --> %s" % (resource.uri,file))
        else:
            urllib.urlretrieve(resource.uri,file)
            if (resource.timestamp is not None):
                unixtime = int(resource.timestamp) #no fractional
                os.utime(file,(unixtime,unixtime))
            self.log_event(ResourceChange(resource=resource, changetype=changetype))


    def parse_sitemap(self):
        s=Sitemap(allow_multifile=self.allow_multifile)
        self.logger.info("Reading sitemap(s) from %s ..." % (self.sitemap))
        i = s.read(self.sitemap)
        num_entries = len(i)
        self.logger.warning("Read sitemap with %d entries in %d sitemaps" % (num_entries,s.sitemaps_created))
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
        s=Sitemap(pretty_xml=True, allow_multifile=self.allow_multifile, mapper=self.mapper)
        if (self.max_sitemap_entries is not None):
            s.max_sitemap_entries = self.max_sitemap_entries
        if (outfile is None):
            print s.resources_as_xml(i,capabilities=i.capabilities)
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
        s = Sitemap(pretty_xml=True, allow_multifile=self.allow_multifile, mapper=self.mapper)
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
        self.logger.info("Writing dump to %s..." % (dump))
        d = Dump(format=self.dump_format)
        d.write(inventory=inventory,dumpfile=dump)

    def read_reference_sitemap(self,ref_sitemap,name='reference'):
        """Read reference sitemap and return the inventory

        name parameter just uses in output messages to say what type
        of sitemap is being read.
        """
        sitemap = Sitemap(allow_multifile=self.allow_multifile, mapper=self.mapper)
        self.logger.info("Reading %s sitemap(s) from %s ..." % (name,ref_sitemap))
        i = sitemap.read(ref_sitemap)
        num_entries = len(i)
        self.logger.warning("Read %s sitemap with %d entries in %d sitemaps" % (name,num_entries,sitemap.sitemaps_created))
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
