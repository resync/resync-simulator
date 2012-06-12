"""ClientInventoryBuilder to create ClientInventory objects from various sources

Attributes:
- do_md5 set true to calculate MD5 sums for all files
- do_size set true to include file size in inventory
- exclude_dirs is a list of directory names to exclude
  (defaults to ['CVS','.git'))
"""

import os
import os.path
from datetime import datetime
from urllib import URLopener
from xml.etree.ElementTree import parse

from client_inventory import ClientInventory
from client_resource import ClientResource
from digest import compute_md5_for_file

class ClientInventoryBuilder():

    def __init__(self, do_md5=False, do_size=True):
        """Create ClientInventoryBuilder object, optionally set options

        Optionaly sets the following attributes:
        - do_md5 - True to add md5 digests for each resource
        - do_size - False to not add size for each resources
        """
        self.do_md5 = do_md5
        self.do_size = do_size
        self.exclude_files = ['sitemap.xml'] #perhaps should be dict for more efficient lookup
        self.exclude_dirs = ['CVS','.git']
        self.include_symlinks = False

    def get(self,url,inventory=None):
        """Get a inventory from url

        Will either create a new ClientInventory object or add to one supplied.
        """
        # Either use inventory passed in or make a new one
        if (inventory is None):
            inventory = ClientInventory()

        inventory_fh = URLopener().open(url)
        #print "got xml:\n" + inventory_xml
        inventory.parse_xml(inventory_fh)
        return(inventory)


    def from_disk(self,path,url_prefix,inventory=None):
        """Create or extend inventory with resources from disk scan

        Assumes very simple disk path to URL mapping: chop path and
        replace with url_path. Returns the new or extended ClientInventory
        object.

        If a inventory is specified then items are added to that rather
        than creating a new one.

        mb = ClientInventoryBuilder()
        m = inventory_from_disk('/path/to/files','http://example.org/path')
        """
        num=0
        # Either use inventory passed in or make a new one
        if (inventory is None):
            inventory = ClientInventory()
        # for each file: create Resource object, add, increment counter
        for dirpath, dirs, files in os.walk(path,topdown=True):
            for file_in_dirpath in files:
                try:
                    if file_in_dirpath in self.exclude_files:
                        continue
                    # get abs filename and also URL
                    file = os.path.join(dirpath,file_in_dirpath)
                    if (not os.path.isfile(file) or not (self.include_symlinks or not os.path.islink(file))):
                        continue
                    rel_path=os.path.relpath(file,start=path)
                    if (os.sep != '/'):
                        # if directory path sep isn't / then translate for URI
                        rel_path=rel_path.replace(os.sep,'/')
                    url = url_prefix+'/'+rel_path
                    file_stat=os.stat(file)
                except OSError as e:
                    sys.stderr.write("Ignoring file %s (error: %s)" % (file,str(e)))
                    continue
                mtime = file_stat.st_mtime
                lastmod = datetime.fromtimestamp(mtime).isoformat()
                r = ClientResource(uri=url,lastmod=lastmod)
                if (self.do_md5):
                    # add md5
                    r.md5=compute_md5_for_file(file)
                if (self.do_size):
                    # add size
                    r.size=file_stat.st_size
                inventory.add(r)
            # prune list of dirs based on self.exclude_dirs
            for exclude in self.exclude_dirs:
                if exclude in dirs:
                    dirs.remove(exclude)
        return(inventory)
