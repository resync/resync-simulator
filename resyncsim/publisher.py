#!/usr/bin/env python

"""
publisher.py: An example publisher who receives change notifications from
the simulator and publish them to external ResourceSync Servers.

Created by Bernhard Haslhofer on 2012-04-02.
Copyright (c) 2012 resourcesync.org. All rights reserved.
"""

import os, re, time, sys
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ElementBase, ET
from sleekxmpp.xmlstream.tostring import tostring
from StringIO import StringIO
from lxml.etree import ElementTree, Element, SubElement
import lxml.etree as etree

from observer import Observer


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

class Bleep(ElementBase):
	name = "url"
	namespace = "http://www.resourcesync.org/ns/"

	def __init__(self, message):
		ElementBase.__init__(self)
		self.xml.text = str(message)

class SimplePublisher(Observer, ClientXMPP):
    """A sample observer that publishes XMPP bleeps"""

    def __init__(self, source, config):
	source.register_observer(self)
	self.config = config

        jid = self.config['jid']
        password = self.config['pwd']
        ClientXMPP.__init__(self, jid, password)
        
        self.node = self.config['pubsub_node']
        self.pubsubjid = self.config['pubsub_jid']
        
        self.ready = False
        self.add_event_handler("session_start", self.session_start)
        self.register_plugin('xep_0060') # PubSub
       
       	print "Connecting as %s" % jid
	sys.stdout.flush()
       	self.connect()
       	self.process(block=False)
       	while not self.ready:
       		time.sleep(0.5)
	

    def notify(self, event):
	print "XMPP publisher received %s. Now it bleeps..." % event
	sys.stdout.flush()

	#XMPP publish if params given
        self.publish(event)


    def session_start(self, event):
        self.send_presence()
        self.ready = True

    def publish(self, msg, node=None, jid=None):
        if not jid:
            jid = self.pubsubjid
        if not node:
            node = self.node
        frm = self.boundjid.user + '@' + self.boundjid.server
            
        blp = Bleep(msg) 
	#
        try:
            self.plugin['xep_0060'].publish(jid, node, payload=blp, ifrom=frm, block=False)
        except IqTimeout:
            print "Timed out for response"
	    sys.stdout.flush()
            return 0
        except IqError:
            print "Something else went wrong"
	    sys.stdout.flush()
            return 0
        return 1


if __name__ == '__main__':
	xmppbleeper = XMPPBleeper()
	print 'called'
        sys.stdout.flush()
	simulator = Simulator(resources = 10, frequency = 3)
	simulator.register_observer(xmppbleeper)
	simulator.run(10)
	#
