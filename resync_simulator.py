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
event_types = ['create', 'delete', 'update', 'all']
p.add_option('--event_types', '-t', choices = simulator.EVENT_TYPES,
             default = simulator.EVENT_TYPES,
             help="the types of change events to be fired (%s)" % event_types)


# Parse command line options and arguments
options, arguments = p.parse_args()

# Run the simulator with all known observers
simulator = simulator.Simulator(options.resources,
                        options.frequency, options.event_types)

simulator.register_observer(XMPPBleeper())
simulator.register_observer(PubsubhubbubBleeper())
simulator.run(10)
    

