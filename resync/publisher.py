#!/usr/bin/env python

"""
publisher.py: An example publisher who receives change notifications from
the simulator and publish them to external ResourceSync Servers.

Created by Bernhard Haslhofer on 2012-04-02.
Copyright (c) 2012 resourcesync.org. All rights reserved.
"""

import os, re, time, sys
import socket

from observer import Observer

from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream.stanzabase import ElementBase

class Publisher(Observer):
    """An abstract publisher implementations that does nothing else than
    providing access to the publisher config and the source"""
    
    def __init__(self, source, config):
        source.register_observer(self)
        self.config = config


class ConsolePublisher(Publisher):
    """A publisher implementation that communicates change events to the
    console."""
    
    def notify(self, event):
        print "Bleep!!!: " + str(event)


class XMPPPublisher(Publisher, ClientXMPP):
    """A publisher that sends change notifications via XMPP"""

    def __init__(self, source, config):
        super(XMPPPublisher, self).__init__(source, config)

        jid = self.config['jid']
        password = self.config['pwd']
        
        ClientXMPP.__init__(self, jid, password)
        
        self.node = self.config['pubsub_node']
        self.pubsubjid = self.config['pubsub_jid']
        
	"""
        print "Testing connection to %s..." % (self.node)
        s = socket.socket()
        port = 80
        try:
            s.connect((self.node, port)) 
        except Exception, e:
            print "Cannnot connect to: %s:%d." % (self.node, port)
            exit(-1)
	"""
        
	self.register_plugin('xep_0030') #discovery
        self.ready = False
        self.add_event_handler("session_start", self.session_start)
        self.register_plugin('xep_0060') # PubSub
       
        print "Connecting to %s as %s" % (self.node, jid)
        sys.stdout.flush()
        self.connect()
        self.process(block=True)
        # while not self.ready:
        #     time.sleep(0.5)

    def notify(self, event):
        print "XMPP publisher received %s. Now it bleeps..." % event
        sys.stdout.flush()
        self.publish(event)

    def session_start(self, event):
        self.send_presence()

	self.go = 0
	try:
		info = self['xep_0030'].get_info(jid=self.pubsubjid, node=self.node, block=True)
		for feature in info['disco_info']['features']:
				if feature == "http://jabber.org/protocol/pubsub":
						print "%s is a pubsub server" % self.pubsubjid
						self.go += 1

		for identity in info['disco_info']['identities']:
				for ident in identity:
						if ident == "pubsub":
								print "%s is a pubsub node" % self.node
								self.go += 1
	except IqError as e:
		print "an error occurred: %s" % e.iq['error']['condition']
		self.diconnect()
	except IqTimeout:
		print "server connection timed out ... exiting!"
		self.diconnect()
	
	if self.go < 2:
		print "A problem occurred, check that the server features PubSub (XEP-0060) and the node is configured accordingly, exiting."
		self.diconnect()
		

        self.ready = True

    def publish(self, msg, node=None, jid=None):
        if not jid:
            jid = self.pubsubjid
        if not node:
            node = self.node
        frm = self.boundjid.user + '@' + self.boundjid.server
            
        blp = Bleep(msg) 

        try:
            self.plugin['xep_0060'].publish(jid, node, payload=blp, ifrom=frm,
                                            block=False)
        except IqTimeout:
            print "Timed out for response"
            sys.stdout.flush()
            return 0
        except IqError:
            print "Something else went wrong"
            sys.stdout.flush()
            return 0
        
        return 1

class Bleep(ElementBase):
    name = "url"
    namespace = "http://www.resourcesync.org/ns/"

    def __init__(self, message):
        ElementBase.__init__(self)
        self.xml.text = str(message)
