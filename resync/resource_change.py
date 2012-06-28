"""Information about a web resource change

Extension of a Resource with change information.
"""

from resource import Resource

class ResourceChange(Resource):
    __slots__=('uri', 'timestamp', 'size', 'md5', 'changeid', 'changetype')
    
    def __init__(self, resource, changeid = None, changetype = None):
        """Create ResourceChange object from a Resource with optional change details"""
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
