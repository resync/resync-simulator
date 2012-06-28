"""Information about a web resource change

Extension of a Resource with change information.
"""

from resource import Resource

class ResourceChange(Resource):
    __slots__=('uri', 'timestamp', 'size', 'md5', 'changeid', 'changetype')
    
    def __init__(self, 
                 # Same interface as Resource
                 uri = None, timestamp = None, size = None, md5 = None, lastmod = None,
                 # Alternative to create from an existing resource, plus extras
                 resource = None, changeid = None, changetype = None):
        """Create ResourceChange object from a Resource with optional change details"""
        super(ResourceChange, self).__init__(uri=uri,timestamp=timestamp,size=size,md5=md5,lastmod=lastmod)
        # Create from a Resource?
        if (resource is not None):
            self.uri = resource.uri
            self.timestamp = resource.timestamp
            self.size = resource.size
            self.md5 = resource.md5
        # Extras for ResourceChange
        self.changeid = changeid
        self.changetype = changetype

    def __str__(self):
        """Return a human readable string for this resource"""
        return "[%s | %s | %d | %s | %s | %s ]" % (self.uri, self.lastmod, self.size,
                                                   self.md5, self.changeid, self.changetype)
