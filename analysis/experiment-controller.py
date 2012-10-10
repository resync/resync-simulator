#!/usr/bin/env python
# encoding: utf-8
"""
experiment-controller.py: Controls the execution of ResourceSync experiments
in a distributed setting.

"""

import os
import sys
import re
import time
import urllib2
from string import Template

CONFIG_TEMPLATE = "template.yaml"

HOSTS = [{'user': 'ubuntu',
          'host': 'ec2-50-17-136-221.compute-1.amazonaws.com',
          'port': 8888
         },
         {'user': 'ubuntu',
          'host': 'ec2-23-21-9-103.compute-1.amazonaws.com',
          'port': 8888,
         }]

# Server addressing

def create_http_uri(host):
    """Constructs an HTTP URI for a certain host"""
    return "http://" + host['host'] + ":" + str(host['port'])

# General remote execution stuff

def execute_remote_command(cmd, host):
    """Executes a given command on a remote host"""
    ssh_connect = "ssh %s@%s" % (host['user'], host['host'])
    cmd = ssh_connect + " " + cmd
    text = os.popen(cmd).read()
    return text

# Simulator-specific operations

def prepare_simulator(host):
    """Prepares simulator (pull recent code, clean deprected files)"""
    print "Preparing simulator at %s" % host
    cmd = "cd simulator; git pull; git checkout dev"
    response = execute_remote_command(cmd, host)
    #print response
    cmd = "cd simulator; rm *.log; rm *.out"
    response = execute_remote_command(cmd, host)
    #print response

def configure_simulator(host, no_resources=1000, change_delay=2):
    """Creates a simulator config file and uploads it to the simulator"""
    fi = open(CONFIG_TEMPLATE, 'r')
    config = fi.read()
    s = Template(config)
    s = s.substitute(no_resources=no_resources, change_delay=change_delay)
    fo = open("default.yaml", 'w')
    fo.write(s)
    cmd = "scp default.yaml %s@%s:~/simulator/config" % (host['user'],
                                                        host['host'])
    text = os.popen(cmd).read()
    print text

def get_simulator_process_id(host):
    """Returns PIDs of currently running simulator processes"""
    cmd = "ps ux | grep simulate-source"
    response = execute_remote_command(cmd, host)
    if len(response) > 0:
        return response.split()[1]
    else:
        return None

def simulator_ready(host):
    """Checks if a simulator is ready ( = HTTP interface is up and running)"""
    try:
        request_uri = create_http_uri(host)
        print "Checking %s ..." % request_uri
        response=urllib2.urlopen(request_uri,timeout=10 )
        return True
    except urllib2.URLError as err: pass
    return False

def stop_simulator(host):
    pid = get_simulator_process_id(host)
    if pid is not None:
        cmd = "kill %s" % pid
        response = execute_remote_command(cmd, host)
        print "Stopping simulator on host %s" % host
    else:
        print "No simulator running at %s" % host

def start_simulator(host):
    print "Starting simulator on host %s" % host
    cmd = "nohup python ./simulator/simulate-source \
            -c simulator/config/default.yaml \
            -n %s -l -e >& /dev/null < /dev/null &" % host
    response = execute_remote_command(cmd, host)
    print "Waiting for simulator startup..."
    while not simulator_ready(host):
        time.sleep(3)
    print "Simulator ready"

# main simulation controller

def run_simulation(no_resources, change_delay, sync_frequency):
    """Runs a simulation with a set of parameters"""
    # Dedicate one host to client and one to server
    source_host = HOSTS[0]
    destination_host = HOSTS[1]
    
    # Stop simulator if running
    stop_simulator(source_host)
    # Prepare simulator
    prepare_simulator(source_host)
    # Configure simulator
    configure_simulator(source_host, no_resources, change_delay)
    # Start simulator
    start_simulator(source_host)
    # Stop simulator
    #stop_simulator(source_host)
    
    print "Finished simulation"

def main():
    """Runs a so"""
    run_simulation(10, 2, 30)
    
if __name__ == '__main__':
   main()                   