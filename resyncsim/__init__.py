"""\
A Python package for running resource synchronization simulations.

This package is intended to provide the core functionality for simulating
a changing Web data source. It defines a configurable simulator that implements
the observer-pattern and send change event notifications to known observers. 
An inventory represents that the state of a data source w.r.t. its resources.

The primary interface of `resyncsim` is `resyncsim.Simulator`.

    >>> import resyncsim
    
    >>> sim = resyncsim.Simulator()
    >>> sim.run()

"""

# Version and last modified date
__version__ = "0.9-dev"
__date__ = "2012/04/02"

__all__ = [
    'Simulator',
    'DEFAULT_RESOURCES',
    'DEFAULT_FREQUENCY',
    'EVENT_TYPES',
    'DEFAULT_EVENT_TYPES',
]

from resyncsim.simulator import Simulator
from resyncsim.simulator import DEFAULT_RESOURCES, DEFAULT_FREQUENCY, \
                                EVENT_TYPES, DEFAULT_EVENT_TYPES
from resyncsim.publisher import XMPPBleeper