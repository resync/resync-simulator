"""ResourceSync inventory object

An inventory is a set of resources with some metadata for each 
resource. Comparison of inventories from a source and a 
destination allows understanding of whether the two are in
sync or whether some resources need to be updated at the
destination.

The inventory object may also contain metadata regarding 
capabilities and discovery information.
"""

import collections
import os
from datetime import datetime
import re
import sys
import StringIO

from resource_container import ResourceContainer
from changeset import ChangeSet
from resource_change import ResourceChange

class InventoryDict(dict):
    """Default implementation of class to store resources in Inventory

    Key properties of this class are:
    - has add(resource) method
    - is iterable and results given in alphanumeric order by resource.uri
    """

    def __iter__(self):
        """Iterator over all the resources in this inventory"""
        self._iter_next_list = sorted(self.keys())
        self._iter_next_list.reverse()
        return(iter(self._iter_next, None))

    def _iter_next(self):
        if (len(self._iter_next_list)>0):
            return(self[self._iter_next_list.pop()])
        else:
            return(None)

    def add(self, resource, replace=False):
        """Add just a single resource"""
        uri = resource.uri
        if (uri in self and not replace):
            raise InventoryDupeError("Attempt to add resource already in inventory") 
        self[uri]=resource

class InventoryDupeError(Exception):
    pass

class Inventory(ResourceContainer):
    """Class representing an inventory of resources

    This same class is used for both the source and the destination
    and is the central point of comparison the decide whether they
    are in sync or what needs to be copied to bring the destinaton
    into sync.

    An inventory will admit only one resource with any given URI.

    Storage is unordered but the iterator imposes a canonical order
    which is currently alphabetical by URI.
    """

    def __init__(self, resources=None, capabilities=None):
        self.resources=(resources if (resources is not None) else InventoryDict())
        self.capabilities=(capabilities if (capabilities is not None) else {})

    def __iter__(self):
        """Iterator over all the resources in this inventory"""
        return(iter(self.resources))

    def add(self, resource, replace=False):
        """Add a resource or an iterable collection of resources

        Will throw a ValueError if the resource (ie. same uri) already
        exists in the inventory, unless replace=True.
        """
        if isinstance(resource, collections.Iterable):
            for r in resource:
                self.resources.add(r,replace)
        else:
            self.resources.add(resource,replace)

    def resource_uris(self):
        """List of the URIs of resources in normal order"""
        return(sorted(self.resources.keys()))

    def changeset(self, uris, changeid=None, changetype=None, replace=False):
        """Create a ChangeSet of ResourceChange objects from a subset of this inventory

        If changeid or changetype is specified then these attributes
        are set in the ResourceChange objects created.
        """
        resources_updated = []
        changeset = ChangeSet()
        for uri in uris:
            rc = ResourceChange( resource=self.resources[uri], changeid=changeid, changetype=changetype )
            changeset.add(rc)
        return(changeset)

    def compare(self,src):
        """Compare the current inventory object with the specified inventory

        The parameter src must also be an inventory object, it is assumed
        to be the source, and the current object is the destination. This 
        written to work for any objects in self and sc, provided that the
        == operator can be used to compare them.

        The functioning of these methods depends on the iterators for self and
        src providing access to the resource objects in URI order.
        """
        # Sort both self and src so that we can then compare in 
        # sequence
        dst_iter = iter(self.resources)
        src_iter = iter(src.resources)
        num_same=0
        updated=[]
        deleted=[]
        created=[]
        dst_cur=next(dst_iter,None)
        src_cur=next(src_iter,None)
        while ((dst_cur is not None) and (src_cur is not None)):
            #print 'dst='+dst_cur+'  src='+src_cur
            if (dst_cur.uri == src_cur.uri):
                if (dst_cur==src_cur):
                    num_same+=1
                else:
                    updated.append(dst_cur)
                dst_cur=next(dst_iter,None)
                src_cur=next(src_iter,None)
            elif (not src_cur or dst_cur.uri < src_cur.uri):
                deleted.append(dst_cur)
                dst_cur=next(dst_iter,None)
            elif (not dst_cur or dst_cur.uri > src_cur.uri):
                created.append(src_cur)
                src_cur=next(src_iter,None)
            else:
                raise InternalError("this should not be possible")
        # what do we have leftover in src or dst lists?
        while (dst_cur is not None):
            deleted.append(dst_cur)
            dst_cur=next(dst_iter,None)
        while (src_cur is not None):
            created.append(src_cur)
            src_cur=next(src_iter,None)
        # have now gone through both lists
        return(num_same,updated,deleted,created)
