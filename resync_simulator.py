#!/usr/bin/env python

"""resync_simulator.py: The ResourceSync Simulator command line interface."""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"

# TODO(behas) Change this to argparse
import optparse
import simulator
from sample_publishers import XMPPBleeper, PubsubhubbubBleeper

# Define simulator options
p = optparse.OptionParser(usage="%prog [options]", version="%prog 0.1")
p.add_option('--resources', '-r', default = simulator.DEFAULT_RESOURCES,
             type = "int", help="the number of seed resources")
p.add_option('--frequency', '-f', default = simulator.DEFAULT_FREQUENCY,
             type = "int",
             help="the number of changes to be simulated per second")
p.add_option('--event_types', '-t', choices = simulator.EVENT_TYPES,
             default = simulator.EVENT_TYPES,
             help="the types of change events to be fired (%s)" % 
                simulator.EVENT_TYPES)


# Parse command line options and arguments
options, arguments = p.parse_args()

# Run the simulator with all known observers
event_types = options.event_types
if isinstance(event_types, basestring):
    event_types = [event_types]

simulator = simulator.Simulator(options.resources,
                        options.frequency, event_types)

simulator.register_observer(XMPPBleeper())
simulator.register_observer(PubsubhubbubBleeper())
#simulator.run(10)
simulator.run()
    

