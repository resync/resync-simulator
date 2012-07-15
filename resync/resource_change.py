"""Information about a web resource change

Extension of a ResourceFile with change information.
"""

from resource_file import ResourceFile

class ResourceChange(ResourceFile):
    __slots__=('uri', 'timestamp', 'size', 'md5', 'file', 'changeid', 'changetype')
    
    def __init__(self, 
                 # Same interface as Resource
                 uri = None, timestamp = None, size = None, md5 = None, lastmod = None,
                 # And ResourceFile
                 resource = None, file = None,
                 # Alternative to create from an existing resource, plus extras
                 changeid = None, changetype = None):
        """Create ResourceChange object from a ResourceFile with optional change details"""
        super(ResourceChange, self).__init__(uri=uri,timestamp=timestamp,size=size,md5=md5,lastmod=lastmod,file=file)
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
        return "[%s | %s | %s | %s | %s | %s | %s ]" % \
               (self.uri, self.lastmod, str(self.size), self.md5, 
                self.file, self.changeid, self.changetype)
