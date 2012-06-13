"""\
A Python package for running resource synchronization simulations.

This package is intended to provide the core functionality for simulating
a changing Web data source. It comprises:
    
    * a 'Source' class to simulate a changing data source
    * an 'HTTPInterface' to the Source
    * a collection of 'Change Memory' implementations
    * a collection of 'Publisher' implementations

The primary interface of `resyncsim` is `resyncsim.Repository`.

    >>> import resync
    
    >>> config = dict(
            number_of_resources = 10,
            change_frequency = 2,
            average_payload = 100,
            event_types = ['create', 'update', 'delete'],
            max_events = 5)
    
    >>> source = resync.Source(config)
    >>> source.simulate_changes()

"""

# Version and last modified date
__version__ = "0.3"
__date__ = "2012/06/13"

__all__ = [
    'Source',
    'HTTPInterface'
]

from resync.source import Source
from resync.http import HTTPInterface
