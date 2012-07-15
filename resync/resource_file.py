"""Information about a local file copy of a web resource

Extension of a Resource with local file information.
"""

from resource import Resource

class ResourceFile(Resource):
    __slots__=('uri', 'timestamp', 'size', 'md5', 'file')
 
    def __init__(self, 
                 # Same interface as Resource
                 uri = None, timestamp = None, size = None, md5 = None, lastmod = None,
                 # Alternative to create from an existing resource, plus extras
                 resource = None, file = None ):
        """Create ResourceFile object from a Resource"""
        super(ResourceFile, self).__init__(uri=uri,timestamp=timestamp,size=size,md5=md5,lastmod=lastmod)
        # Create from a Resource?
        if (resource is not None):
            self.uri = resource.uri
            self.timestamp = resource.timestamp
            self.size = resource.size
            self.md5 = resource.md5
        # Extras for ResourceFile
        self.file = file

    def __str__(self):
        """Return a human readable string for this resource"""
        return "[%s | %s | %s | %s | %s ]" % (self.uri, self.lastmod, str(self.size),
                                              self.md5, self.file )
