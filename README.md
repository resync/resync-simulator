# ResourceSync Simulator

The ResourceSync Simulator simulates a changing data source. Currently, it supports **create**, **update**, and **delete** events.

The simulator implements the Observer Pattern, which means that the simulator notifies a number of registered observers about change events. It takes the following parameters:

* resources: the number of seed resources contained in the data sources inventory (default: 100)
* frequency: the number of events per second (default: 1)
* event type(s): what kind of events it should simulate (default: ALL)
* simulations: the number of simulations to run (default: infinite)

## Install

Install the [Tornado](http://www.tornadoweb.org/) web server library:

    easy_install tornado
    
Get the ResourceSync Simulator from [Github](http://www.github.com/behas/resync-simulator):

    git clone git://github.com/behas/resync-simulator.git


## Command Line Usage

Change to the ResourceSync Simulator directory and make sure that the start script is executable:

    cd resync-simulator
    chmod u+x rs-simulator

Run the simulator with default settings:

    ./rs-simulator
    
... and view the changing inventory at: http://localhost:8888
    
Publish events to registered publishers

    ./rs-simulator -p
    
Run 5 simulation iterations with 10 seed resources, a frequency of 2 events per second, and only create events

    ./rs-simulator -p -s 5 -r 10 -f 2 -t create

Terminate simulation when running in infinite mode:

    CTRL-C