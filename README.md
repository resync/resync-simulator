# ResourceSync Simulator

The ResourceSync Simulator simulates a changing Web data source.

A client is provided to synchronize a filesystem directory with the simulated resources.

## Quick start

Make sure Python 2.7.1 is running on your system:

    python --version

Install the [Tornado](http://www.tornadoweb.org/) and [SleekXMPP](https://github.com/fritzy/SleekXMPP) libraries:

    sudo easy_install tornado
    sudo easy_install sleekxmpp    
    sudo easy_install PyYAML
    
Get the ResourceSync Simulator from [Github](http://www.github.com/behas/resync-simulator):

    git clone git://github.com/resync/simulator.git
    
Run the source simulator (with the default configuration in /config/default.yaml):
    
    chmod u+x simulate-source
    ./simulate-source

Run the resync client against the simulated source

    chmod u+x resync-client
    ./resync-client http://localhost:8888/sitemap.xml /tmp/sim 

Terminate the source simulator:

    CTRL-C


## How to define parameterized use cases

Parameterized Use Cases can be defined by creating a configuration file **config/example.yaml** and defining a set of parameters:

    source:
        name: Morvania National Library
        number_of_resources: 20000
        change_frequency: 0.5
        event_types: [create, update, delete]
        average_payload: 10000
        max_events: -1
        
Additional **publisher** and **change memory** implementations
can be attached for simulation purposes. For instance, the following configuration attaches a change memory implemented in the DynamicChangeSet class.

    changememory:
        class: DynamicChangeSet
        uri_path: /changes

See the examples in the /config directory for further details.


## How to implement custom inventories, change memories, publishers, etc.

Implement your code, encapsulated in python objects, directly in the following files:

* publisher.py
* changememory.py

Run the simulator with your custom implementation by defining the classname in a configuration file and pass it to the main simulator script:

    ./simulate-source -c config/myusecase.yaml

## How to run the simulator with the XMPP publisher

Define the necessary XMPP settings in a config file and run the simulator, e.g.:

    ./simulate-source -c config/example_xmpp.yaml
