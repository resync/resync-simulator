resync-simulator change log
===========================

2017-04-13 v1.0.2
  * fix MD5 sum format
  * update for resync v1.0.7 library
  * drop python 2.6 support

2016-05-06 v1.0.1
  * supports v1.0 ResourceSync specification 
  * tested with resync v1.0.2 library
  * adopt versioning scheme similar to resync
  * tidy code, add trive tests
     
2013-09-06 v0.7
  * updated for v0.9.1 ResourceSync specification
  * updated to use resync v0.9.3 library

2013-05-14 v0.6
  * implemented simulator with resync v0.6.2 library
  * dead code parts cleanup

2013-05-07 v0.5
  * removed experimental code
  * removed dynamic changememory based on changeid
  * removed static changememory builder (which needs to be re-written)
  * tested with current resync client master

2012-08-24 v0.4
  * implemented static changememory
  * added max events restriction to changememory
  * implemented changesets (client side)
  * implemented dump (client side)
  * added static sitemap creation option to simulator
  * unified simulator and client sitemap creation

2012-06-13 v0.3
  * unified client and source inventory implementation
  * wired dynamic inventory with changememory
  * implemented Dynamic ChangeSet according to draft specification
  * add resync-client for baseline synchronization
  * added XMPP publisher implementation
  * Generalized resource.py for re-use on client and server side
  * Added change memory with paging implementation

2012-05-08 v0.2
  * Implemented command line publisher
  * Implemented dynamic digest
  * Implemented dynamic sitemap inventory
  * Implemented reflective loading of simulation components
  * Modularized architecture: source - inventory - change memory - publisher
  * Implemented command line eventlog
  * Extracted change model into separate module
  * Merged simulator and inventory logic into "source"
  * Cleaned up simulation configuration; switched to YAML

2012-04-04 v0.1
  * Initial release supporting basic simulation, observer interface, sitemap
  generation, and a simple Web interface.