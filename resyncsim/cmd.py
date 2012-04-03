#!/usr/bin/env python
# encoding: utf-8
"""
cmd.py: The ResourceSync Simulator command line interface.

Created by Bernhard Haslhofer on 2012-04-02.
Copyright (c) 2012 resourcesync.org. All rights reserved.
"""

import optparse
import simulator

def main():
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

    sim = simulator.Simulator(options.resources,
                            options.frequency, event_types)

    print sim.inventory
    sim.run(10)
    print sim.inventory
    #sim.run()


if __name__ == '__main__':
	main()