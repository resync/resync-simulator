#!/usr/bin/env python

import optparse





def main():
    p = optparse.OptionParser(usage="%prog [options]", version="%prog 0.1")
    p.add_option('--resources', '-r', default=1000,
                 type = "int", help="the number of seed resources")
    p.add_option('--frequency', '-f', default = 1,
                 type = "int",
                 help="the number of changes to be simulated per second")
    event_types = ['create', 'delete', 'update', 'all']
    p.add_option('--event-type', '-t', choices = event_types,
                 help="the change event types to be fired (%s)" % event_types)
    options, arguments = p.parse_args()
    
    print 'Run Simulator with %d resources, firing change events %d times ' \
          'per second.' % (options.resources, options.frequency)
    

if __name__ == '__main__':
    main()

