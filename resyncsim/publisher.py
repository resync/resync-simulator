#!/usr/bin/env python

"""
publisher.py: An example publisher who receives change notifications from
the simulator and publish them to external ResourceSync Servers.

Created by Bernhard Haslhofer on 2012-04-02.
Copyright (c) 2012 resourcesync.org. All rights reserved.
"""

from simulator import Simulator
from observer import Observer

class XMPPBleeper(Observer):
    """A sample observer that publishes XMPP bleeps"""
    
    def notify(self, event):
        print "XMPP publisher received %s. Now it bleeps..." % event
        


if __name__ == '__main__':
    xmppbleeper = XMPPBleeper()
    simulator = Simulator(resources = 10, frequency = 3)
    simulator.register_observer(xmppbleeper)
    simulator.run(10)

