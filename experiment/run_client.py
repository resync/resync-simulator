#!/usr/bin/env python

import ConfigParser
import optparse
import datetime
import time
import os
import subprocess
import sys

p = optparse.OptionParser(description='Run ResourceSync Expts')
p.add_option('--run', '-r', type="str", action='store',
             help='Name of config to run')
p.add_option('--stdout', '-s', action='store_true',
             help='Do not send output to file, leave on stdout')
(args, map) = p.parse_args()
run = args.run

config = ConfigParser.RawConfigParser()
config.read('expt.cfg')

client   = config.get(run, 'client')
interval = config.getint(run, 'interval')
repeat   = config.getint(run, 'repeat')
url      = config.get(run, 'url')
path     = run+'_data'
log      = run+'_log'

#unbuffer stdout
if (args.stdout):
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
else:
    # send to file
    sys.stdout = open( run+'_stdout', 'w', 0)

if (not os.path.isdir(path)):
    os.mkdir(path)

print "Going to sync with %s -> %s, %d times with %d s interval" %\
    ( url, path, repeat, interval )

for n in range(0,repeat):
    if (n>0):
        print "\ngoing to sleep for %d s" % (interval)
        time.sleep(interval)
    print "\n[%d] %s" % (n, datetime.datetime.now() ) 
    cmd = [ client, '--sync','--delete', '--eval',
            '--logger', '--logfile', log,
            url, path ]
    print "Running:" + ' '.join(cmd)
    subprocess.call(cmd, stderr=sys.stdout)

print "Done."
