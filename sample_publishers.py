#!/usr/bin/env python

"""simulator.py: A collection of sample bleepers which receive change events
from the simulator.
"""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"


from simulator import Simulator
from observer import Observer

class XMPPBleeper(Observer):
    
    def notify(self, event):
        print "Cool...got a notification. Now I XMPP bleep bleep bleep..."
        
        
class PubsubhubbubBleeper(Observer):
    
    def notify(self, event):
        print "Wow...me too. Now I pubsubhubbubbubssubhbubub...."



if __name__ == '__main__':
    xmppbleeper = XMPPBleeper()
    pubsubbleeper = PubsubhubbubBleeper()
    simulator = Simulator(resources = 10, frequency = 3)
    simulator.register_observer(xmppbleeper)
    simulator.register_observer(pubsubbleeper)
    simulator.run(10)

