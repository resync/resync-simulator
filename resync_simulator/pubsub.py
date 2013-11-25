"""
pubsub.py: PubSubHubub hub-client interface for ResourceSync simulator

Simeon Warner, 2013-11-23
"""

import os
import random
import pprint
import logging
import time
import thread   #FIXME - for kludge only
import threading

from resync.utils import compute_md5_for_string

class PubSubInterface(threading.Thread):
    """Wrapper to run a source in a separate thread"""

    def __init__(self, source=None):
        threading.Thread.__init__(self)
        self.source = source
        self._stop = threading.Event()
        self.stop_flag = 0;

    def setup(self):
        print "Setting up PubSub interface"

    def run(self):
        while (self.stop_flag==0):
            print "pubsub running"
            time.sleep(2)
            self.send_updates()

    def stop(self):
        # Call this to signal to this thread to stop
        self._stop.set()
        self.stop_flag = 1 # flag exit request, why doesn't even above work?
        #print "set stop_flag=%d" % self.stop_flag

    def send_updates(self):
        cl = self.source.changememory.generate_incremental()
        cl.pretty_xml = True
        cl.up = self.source.base_uri + "/capabilitylist.xml"
        if (cl and len(cl)>0):
            print cl.as_xml()
