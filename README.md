# ResourceSync Simulator

The ResourceSync Simulator simulates a changing Web data source.

It follows a modular architecture comprising a few core building blocks:

* source.py: the changing data source
* inventory.py: a collection of inventory implementations
* publisher.py: a collection of change publishers that send out notifications
* changememory.py: a collection of change memory implementations


## Quick start

Make sure Python 2.7.1 is running on your system:

    python --version

Install the [Tornado](http://www.tornadoweb.org/) web server library:

    sudo easy_install tornado
    
Get the ResourceSync Simulator from [Github](http://www.github.com/behas/resync-simulator):

    git clone git://github.com/behas/resync-simulator.git
    
Run the simulation (with the default configuration in /config/default.yaml):
    
    chmod u+x simulate-source
    ./simulate-source

Terminate simulation when running in infinite mode:

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
        
Additional **inventory**, **publisher**, and **change memory** implementations
can be attached for simulation purposes. For instance, the following configuration attaches the *DynamicSiteMapInventory* inventory implementation and passes the given parameters (url) to that implementation.

    inventory:
        class: DynamicSiteMap
        url: /sitemap.xml

See the examples in the /config directory for further details.


## How to implement custom inventories, change memories, publishers, etc..

Implement your code, encapsulated in python objects, directly in the following files:

* inventory.py
* publisher.py
* changememory.py

Run the simulator with your custom implementation by defining the classname in a configuration file and pass it to the main simulator script:

    ./simulate-source -c config/myusecase.yaml
