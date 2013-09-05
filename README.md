======================
ResourceSync Simulator
======================

The ResourceSync Simulator simulates a [ResourceSync](http://www.openarchives.org/rs/0.9.1/resourcesync) Source, which is a server that hosts resources subject to synchronization.

Any ResourceSync-compliant client can be used to synchronize a Destination with the simulated Source. The simulator is tested with v0.9.3 of our own [ResourceSync client and library reference implementationn](https://github.com/resync/resync).


Quick start
-----------

Make sure Python 2.7.2 or later is running on your system:

    python --version

Install the [resync](https://github.com/resync/resync) library
code and the [Tornado](http://www.tornadoweb.org/) web server:

    sudo easy_install resync
    sudo easy_install tornado
    
Get the ResourceSync Simulator from [Github](http://www.github.com/resync/simulator):

    git clone git://github.com/resync/simulator.git
    
Run the source simulator (with the default configuration in ./config/default.yaml):
    
    chmod u+x resync-simulator
    ./resync-simulator

Terminate the source simulator:

    CTRL-C

How to define parameterized use cases
-------------------------------------

Parameterized Use Cases can be defined by creating a [YAML](http://www.yaml.org/) configuration file (e.g., simulation1.yaml) and defining a set of parameters:

    source:
        name: ResourceSync Simulator
        number_of_resources: 1000
        change_delay: 2
        event_types: [create, update, delete]
        average_payload: 1000
        max_events: -1
        stats_interval: 10
        
Additional **resource_list_builder** and **change memory** implementations can be attached for simulation purposes. For instance, the following configuration attaches a change memory implemented by the DynamicChangeList class.

    resource_list_builder:
        class: DynamicResourceListBuilder
        uri_path: resourcelist.xml

    changememory:
        class: DynamicChangeList
        uri_path: changelist.xml
        max_changes: 1000
            
See the examples in the **./config** directory for further details.

See also
--------

`ResourceSync library
<http://github.com/resync/resync>`_

Author and Contributors
-----------------------

Author:
`Bernhard Haslhofer
<https://github.com/behas>`_

Contributors:
`Simeon Warner
<https://github.com/zimeon>`_
