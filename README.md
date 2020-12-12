# ResourceSync Simulator

[![Build status](https://travis-ci.org/resync/resync-simulator.svg?branch=master)](https://travis-ci.org/resync/resync-simulator)
[![Test coverage](https://coveralls.io/repos/github/resync/resync-simulator/badge.svg?branch=master)](https://coveralls.io/github/resync/resync-simulator?branch=master)

The ResourceSync Simulator simulates a [ResourceSync](http://www.openarchives.org/rs) Source, which is a server that hosts resources subject to synchronization.

Any ResourceSync-compliant client can be used to synchronize a Destination with the simulated Source. This version of the simulator is written against v1.0 of the [ResourceSync specification](http://www.openarchives.org/rs/1.0) and has been tested with v1.0.9 of our own [ResourceSync client and library reference implementation](https://github.com/resync/resync).

## Installation

This simulator is designed to run under Python 3. Check with

```
python --version
```

### Automatic installation

```
pip install resync-simulator
```

`rsync-simulator` is listed in [PyPI](http://pypi.python.org/pypi/resync-simulator) and can be installed with `pip` or `easy_install`. Either installation method should also dependencies if they are not already on your system.


### Manual installation from github

Install the [resync](https://github.com/resync/resync) library code and the [Tornado](http://www.tornadoweb.org/) web server (you might need to use `sudo` depending on you local setup)

```
pip install resync tornado
```

Get the ResourceSync Simulator from [Github](http://www.github.com/resync/resync-simulator)

```
git clone git://github.com/resync/resync-simulator.git
```

## Quick Start

Run the source simulator (with the default configuration in `./config/default.yaml`

```
./resync-simulator
```

Access from a web browser as <http://localhost:8888/>

Terminate the source simulator with `CTRL-C`


## How to define parameterized use cases

Parameterized Use Cases can be defined by creating a [YAML](http://www.yaml.org/) configuration file (e.g., `simulation1.yaml` and defining a set of parameters

```
source:
    name: ResourceSync Simulator with 1000 resources
    number_of_resources: 1000
    change_delay: 2
    event_types: [create, update, delete]
    average_payload: 1000
    max_events: -1
    stats_interval: 10
````

Additional **resource_list_builder** and **change memory** implementations can be attached for simulation purposes. For instance, the following configuration attaches a change memory implemented by the `DynamicChangeList` class

```
resource_list_builder:
    class: DynamicResourceListBuilder
    uri_path: resourcelist.xml

changememory:
    class: DynamicChangeList
    uri_path: changelist.xml
    max_changes: 1000
```

See the examples in the `./config` directory for further details.


## See also

  * [ResourceSync library](http://github.com/resync/resync)


## Author and Contributors

Author: [Bernhard Haslhofer](https://github.com/behas)

Contributors: [Simeon Warner](https://github.com/zimeon)
