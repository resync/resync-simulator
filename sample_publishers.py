#!/usr/bin/env python

"""simulator.py: A collection of sample which receive change events
from the simulator and publish them to external ResourceSync Servers.
"""

__author__      = "Bernhard Haslhofer"
__copyright__   = "Copyright 2012, ResourceSync.org"


from simulator import Simulator
from observer import Observer

class XMPPBleeper(Observer):
    """A sample observer that publishes XMPP bleeps"""
    
    def notify(self, event):
        print "XMPP publisher received %s. Now it bleeps..." % event
        
        
class PubsubhubbubBleeper(Observer):
    
    def notify(self, event):
        print "Pubsubhubbub publisher received %s. Now it pubsubs...." % event


if __name__ == '__main__':
    xmppbleeper = XMPPBleeper()
    pubsubbleeper = PubsubhubbubBleeper()
    simulator = Simulator(resources = 10, frequency = 3)
    simulator.register_observer(xmppbleeper)
    simulator.register_observer(pubsubbleeper)
    simulator.run(10)

