#!/usr/bin/env python
# encoding: utf-8
"""
experiment-controller.py: Controls the execution of ResourceSync experiments
in a distributed setting.

Overall strategy:
    - choose host pairs with simulator installed
    - start simulator at one host; start client sync process at the other
    - terminate client and simulator after given time X
    - pull down log files; record simulation settings / file mappings
    - start again
    
Simulation hosts: Amazon EC2 images

Contoller hosts: Cornell VM or Uni Vienna image
    
"""

import os
import subprocess
import sys
import re
import time
import urllib2
from string import Template
import csv

CONFIG_TEMPLATE = "template.yaml"

SSH_KEY = "resync.pem"

HOSTS = [{'user': 'ubuntu',
          'host': 'ec2-107-22-85-123.compute-1.amazonaws.com',
          'port': 8888
         },
         {'user': 'ubuntu',
          'host': 'ec2-107-22-148-244.compute-1.amazonaws.com',
          'port': 8888,
         }]

#  Operations common to all tasks

def create_http_uri(host):
    """Constructs an HTTP URI for a certain host"""
    return "http://" + host['host'] + ":" + str(host['port'])

def execute_remote_command(cmd, host):
    """Executes a given command on a remote host"""
    ssh_connect = "ssh -i %s %s@%s" % (SSH_KEY, host['user'], host['host'])
    cmd = ssh_connect + " " + "\"" + cmd + "\""
    text = os.popen(cmd).read()
    return text.strip()

def copy_file_to_remote(local_file, remote_path, host):
    """Copies a local file to a remote host path"""
    subprocess.Popen(['scp', '-i', SSH_KEY, local_file,
        '%s@%s:%s' % (host['user'],host['host'],remote_path)]).wait()

def copy_file_from_remote(remote_path, local_file, host):
    """Copies a remote to a local file"""
    subprocess.Popen(['scp', '-i', SSH_KEY, 
        '%s@%s:%s' % (host['user'],host['host'],remote_path),local_file]).wait()


# Experiment tasks

def reset_host(host):
    """Prepare host (kill processes, clean files, pull recent code)"""
    print "*** Resetting host %s ***" % host['host']
    print execute_remote_command("cd simulator; git pull", host)
    print execute_remote_command("rm *.log", host)
    print execute_remote_command("rm *.out", host)
    print execute_remote_command("killall python", host)
    print execute_remote_command("rm -rf /tmp/sim", host)

def configure_source(host, no_resources=1000, change_delay=2):
    """Creates a simulator config file and uploads it to the simulator"""
    print "*** Configuring source host at %s ***" % host['host']
    CONFIG_FILE = "default.yaml"
    fi = open(CONFIG_TEMPLATE, 'r')
    config = fi.read()
    s = Template(config)
    s = s.substitute(no_resources=no_resources, change_delay=change_delay)
    fo = open(CONFIG_FILE, 'w')
    fo.write(s)
    fo.close()
    copy_file_to_remote(CONFIG_FILE, "~/simulator/config", host)
    
def start_source_simulator(host):
    print "*** Starting source simulator on host %s ***" % host['host']
    cmd = "nohup python ./simulator/simulate-source \
            -c simulator/config/default.yaml \
            -n %s -l -e >& /dev/null < /dev/null &" % host['host']
    response = execute_remote_command(cmd, host)
    print "Waiting for simulator startup..."
    simulator_ready = False
    while not simulator_ready:
        time.sleep(3)
        try:
            request_uri = create_http_uri(host)
            print "Checking %s ..." % request_uri
            response=urllib2.urlopen(request_uri,timeout=10 )
            simulator_ready = True
        except urllib2.URLError as err:
            simulator_ready = False
    print "Simulator ready"

def start_synchronization(destination_host, source_host):
    print "*** Starting synchronization on host %s ***" % destination_host['host']
    cmd = [ 'python', './simulator/resync-client', 
            '--sync','--delete', '--eval','--logger',
            '--logfile', 'resync-client.log',
            create_http_uri(source_host), "/tmp/sim"]
    print "Running:" + ' '.join(cmd)
    print execute_remote_command(' '.join(cmd), destination_host)

def stop_source_simulator(host):
    print "*** Stopping source simulator ***"
    print execute_remote_command("killall python", host)
    

def download_results(settings, dst_path="./data"):
    print "*** Downloading and keeping track of simulation logs ***"

    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    file_hash = hash(time.time())
    source_dst_file = dst_path + "/" + "resync_src_%s.log" % file_hash
    dst_dst_file = dst_path + "/" + "resync_dst_%s.log" % file_hash
    
    copy_file_from_remote("~/resync-source.log", source_dst_file,
                          settings['source_host'])
    copy_file_from_remote("~/resync-client.log", dst_dst_file,
                          settings['destination_host'])
                          
    csv_file_name = dst_path + "/simulations.csv"
    if not os.path.exists(dst_path):
        write_header = True
    else:
        write_header = False
    
    with open(csv_file_name, 'a') as csv_file:
        writer = csv.writer(csv_file)
        if write_header:
            writer.writerows(
                ['id','src_host', 'dst_host', 'no_resources', 'change_delay'])
        writer.writerows([settings['id'], settings['source_host']])
    
    
# main simulation controller

def run_simulation(settings):
    """Runs a simulation with a set of parameters"""
    
    # Check if SSH identity key is available
    try:
       with open(SSH_KEY) as f: pass
    except IOError as e:
       print 'SSH identity file (%s) not found.' % SSH_KEY
       sys.exit(-1)
    
    print "Starting simulation..."
    print "\tsource: %s" % settings['source_host']
    print "\tdestination: %s" % settings['destination_host']
    print "\tno_resources: %d" % settings['no_resources']
    print "\tchange_delay: %d" % settings['change_delay']
    print "\tsync_interval: %d" % settings['sync_interval']
    
    # Reset hosts
    reset_host(settings['source_host'])
    reset_host(settings['destination_host'])
    # Prepare source
    configure_source(settings['source_host'],
                     settings['no_resources'],
                     settings['change_delay'])
    # Start simulator
    start_source_simulator(settings['source_host'])
    # Start synchronization at destination
    start_synchronization(settings['destination_host'],
                          settings['source_host'])
    # Stop simulator
    stop_source_simulator(settings['source_host'])
    # Download result files
    download_results(settings)
    # Summarize results files
    print "*** Finished simulation ***"

def main():
    """Runs a single simulation iteration"""
    settings = {}
    settings['id'] = 1
    settings['source_host'] = HOSTS[0]
    settings['destination_host'] = HOSTS[1]
    settings['no_resources'] = 10
    settings['change_delay'] = 2
    settings['sync_interval'] = 30
    run_simulation(settings)
    
if __name__ == '__main__':
   main()                   