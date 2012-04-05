# ResourceSync Change Simulator

The ResourceSync Change Simulator simulates a changing data source

Currently the following types of change events are supported:

* create
* update
* delete

...and the following parameters:

* resources: the number of seed resources contained in the data sources inventory (default: 100)
* frequency: the number of events per second (default: 1)
* event type(s): what kind of events it should simulate (default: ALL)
* simulations: the number of simulations to run (default: infinite)

The simulator implements the [observer][Observer Pattern], which means that the simulator notifies a number of registered observers about change events.

## Command Line Usage

Run the simulator with default settings:

    ./rs-simulator
    
... and view the changing inventory at: http://localhost:8888
    
Publish events to registered publishers

    ./rs-simulator -p
    
Run 5 simulation iterations with 10 seed resources, a frequency of 2 events per second, and only create events

    ./rs-simulator -p -s 5 -r 10 -f 2 -t create

Terminate simulation when running in infinite mode:

    CTRL-C

    
[observer](http://en.wikipedia.org/wiki/Observer_pattern)