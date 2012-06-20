"""ResourceSync inventory object

An inventory is a set of resources with some metadata for each 
resource. Comparison of inventories from a source and a 
destination allows understanding of whether the two are in
sync or whether some resources need to be updated at the
destination.

The inventory object may also contain metadata regarding capabilities
and discovery information.
"""
import os
from datetime import datetime
import re
import sys
import StringIO

from resource import Resource

class InventoryDupeError(Exception):
    pass

class Inventory(object):
    """Class representing an inventory of resources

    This same class is used for both the source and the destination
    and is the central point of comparison the decide whether they
    are in sync or what needs to be copied to bring the destinaton
    into sync.

    An inventory will admit only one resource with any given URI.
    """

    def __init__(self, resources=None, capabilities=None):
        self.resources=(resources if (resources is not None) else {})
        self.capabilities=(capabilities if (capabilities is not None) else {})

    def __len__(self):
        return len(self.resources)

    def add(self, resource, replace=False):
        """Add a resource to this inventory

        Will throw a ValueError is the resource (ie. same uri) already
        exists in the inventory, unless replace=True.
        """
        uri = resource.uri
        if (uri in self.resources and not replace):
            raise InventoryDupeError("Attempt to add resource already in inventory") 
        self.resources[uri]=resource

    def compare(self,src):
        """Compare the current inventory object with the specified inventory

        The parameter src must also be an inventory object, it is assumed
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
                
    def __str__(self):
        """Return string of all resources sorted by URI"""
        s = ''
        for uri in sorted(self.resources.keys()):
            s += str(self.resources[uri]) + "\n"
        return(s)
