"""Extension of Resource that add changeid

Add changeid attribute as an extra __slot__.
"""

from resync.resource import Resource as BaseResource

class Resource(BaseResource):
    __slots__=('changeid')
