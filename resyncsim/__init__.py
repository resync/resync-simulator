"""\
A Python package for running resource synchronization simulations.

This package is intended to provide the core functionality for simulating
a changing Web data source. It comprises:
    
    * a REPOSITORY class to simulate changes
    * a variety of possible INVENTORY and CHANGEMEMORY implementations


The primary interface of `resyncsim` is `resyncsim.Repository`.

    >>> import resyncsim
    
    >>> source = resyncsim.Source()
    >>> source.simulate_changes()
s
"""

# Version and last modified date
__version__ = "0.2-dev"
__date__ = "2012/05/01"

__all__ = [
    'Source',
    'ConsoleEventLog'
]

from resyncsim.source import Source
from resyncsim.event_log import ConsoleEventLog