"""\
A Python package for running resource synchronization simulations.

This package is intended to provide the core functionality for simulating
a changing Web data source. It comprises:
    
    * a 'Source' class to simulate a changing data source
    * an 'HTTPInterface' to the Source
    * a collection of 'Inventory' implementations
    * a collection of 'Change Memory' implementations
    * a collection of 'Publisher' implementations

The primary interface of `resyncsim` is `resyncsim.Repository`.

    >>> import resyncsim
    
    >>> config = dict(
            number_of_resources = 10,
            change_frequency = 2,
            average_payload = 100,
            event_types = ['create', 'update', 'delete'],
            max_events = 5)
    
    >>> source = resyncsim.Source(config)
    >>> source.simulate_changes()

"""

# Version and last modified date
__version__ = "0.2"
__date__ = "2012/05/09"

__all__ = [
    'Source',
    'HTTPInterface'
]

from resyncsim.source import Source
from resyncsim.http import HTTPInterface
