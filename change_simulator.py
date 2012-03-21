#!/usr/bin/env python

import time

class ChangeSimulator:
    
    EVENT_TYPES = ['create', 'update', 'delete']
    
    DEFAULT_RESOURCES = 1000
    DEFAULT_FREQUENCY = 1
    DEFAULT_EVENT_TYPES = EVENT_TYPES
    
    """This class simulates ResourceSync changes on a set of resources"""
    def __init__(self,
                resources = DEFAULT_RESOURCES,
                frequency = DEFAULT_FREQUENCY,
                event_types = DEFAULT_EVENT_TYPES):
        self.resources = resources
        self.frequency = frequency
        self.event_types = event_types
        print 'Setting up ChangeSimulator with %d resources, ' \
              'firing the following types of change events %d times ' \
              'per second: %s' % (self.resources, self.frequency,
                                  self.event_types)
    
    def run(self):
        """Starts the simulator"""
        sleep_time = round(float(1) / self.frequency, 2)
        while True:
            time.sleep(sleep_time)
            print "Doing something at %s" % time.time() 
    
        
if __name__ == '__main__':
    simulator = ChangeSimulator(frequency = 2)
    simulator.run()
