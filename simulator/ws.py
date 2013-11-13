import tornado.ioloop
from tornado.web import Application
from tornado.websocket import WebSocketHandler

class WSInterface(Application):
    def __init__(self):    
        handlers = [(r"/cf", ResyncSocketHandler)]
        Application.__init__(self, handlers, {})

class ResyncSocketHandler(WebSocketHandler):
    destinations = set()
    def open(self):
        ResyncSocketHandler.destinations.add(self)
    def on_close(self):
        ResyncSocketHandler.destinations.remove(self)
    @classmethod
    def send_updates(cls, msg, frm=None):
        for dest in cls.destinations:
            if dest != frm:
                try:
                    dest.write_message(msg)
                except:
                    pass # logging goes here
