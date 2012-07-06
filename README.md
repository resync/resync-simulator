# ResourceSync Simulator

The ResourceSync Simulator simulates a changing Web data source.

A client is provided to synchronize a filesystem directory with the simulated resources.

## Quick start

Make sure Python 2.7.1 is running on your system:

    python --version

Install the [Tornado](http://www.tornadoweb.org/) and [SleekXMPP](https://github.com/fritzy/SleekXMPP), [PyYAML](http://pyyaml.org/), and [APScheduler](http://packages.python.org/APScheduler/) libraries:

    sudo easy_install tornado
    sudo easy_install sleekxmpp    
    sudo easy_install PyYAML
    sudo easy_install apscheduler
    
Get the ResourceSync Simulator from [Github](http://www.github.com/behas/resync-simulator):

    git clone git://github.com/resync/simulator.git
    
Run the source simulator (with the default configuration in /config/default.yaml):
    
    chmod u+x simulate-source
    ./simulate-source

Run the resync client against the simulated source

    chmod u+x resync-client
    ./resync-client http://localhost:8888 /tmp/sim 

Terminate the source simulator:

    CTRL-C


## How to define parameterized use cases

Parameterized Use Cases can be defined by creating a [YAML](http://www.yaml.org/) configuration file (e.g., example.yaml) and defining a set of parameters:

    source:
        name: ResourceSync Simulator
        number_of_resources: 1000
        change_delay: 2
        event_types: [create, update, delete]
        average_payload: 1000
        max_events: -1
        
Additional **inventory**, **publisher**, and **change memory** implementations
can be attached for simulation purposes. For instance, the following configuration attaches a change memory implemented in the DynamicChangeSet class.

    inventory:
        class: StaticSourceInventory
        max_sitemap_entries: 500
        interval: 15
        uri_path: sitemap.xml

    changememory:
        class: DynamicChangeSet
        uri_path: /changes

See the examples in the **/config** directory for further details.