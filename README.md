# ResourceSync Change Simulator

The ResourceSync simulates change events in a data source.

Currently it supports the following types of events

* create
* update
* delete

...and the following parameters:

* resources: the number of seed resources contained in the data sources inventory (default: 100)
* frequency: the number of events per second (default: 1)
*  event type(s): what kind of events it should simulate (default: ALL)

The simulator implements the [observer][Observer Pattern], which means that the simulator notifies a number of registered observers about change events.

## Command Line Usage

Start the command line simulator with default settings:

    python resync_simulator.py
    
List available options

    python resync_simulator.py -h
    
Run the simulator with 1000 seed resources, a frequency of 3 events per second, and only create events

    python resync_simulator.py -r 1000 -f 3 -t create
    
## API Usage

Extend the simulator with additional publisher clients by extending the *Observer* class and implementing the *notify(self, event)* method. Here is an example:

    from simulator import Simulator
    from observer import Observer

    class XMPPBleeper(Observer):
        """A sample observer that publishes XMPP bleeps"""
    
        def notify(self, event):
            print "XMPP publisher received %s. Now it bleeps..." % event

[observer](http://en.wikipedia.org/wiki/Observer_pattern)