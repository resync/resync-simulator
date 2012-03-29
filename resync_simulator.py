#!/usr/bin/env python

import optparse

import simulator

def main():
    p = optparse.OptionParser(usage="%prog [options]", version="%prog 0.1")
    p.add_option('--resources', '-r', default=1000,
                 type = "int", help="the number of seed resources")
    p.add_option('--frequency', '-f', default = 1,
                 type = "int",
                 help="the number of changes to be simulated per second")
    event_types = ['create', 'delete', 'update', 'all']
    p.add_option('--event_type', '-t', choices = simulator.EVENT_TYPES,
                 default = simulator.EVENT_TYPES,
                 help="the change event types to be fired (%s)" % event_types)
    options, arguments = p.parse_args()
    
    print options
    
    # TODO: init simulator
    

if __name__ == '__main__':
    main()

