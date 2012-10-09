#!/usr/bin/env python
# encoding: utf-8
"""
experiment-controller.py: Controls the execution of ResourceSync experiments
in a distributed setting.

"""

import os
import re

source_user = "ubuntu"
source_hosts = ["ec2-50-17-136-221.compute-1.amazonaws.com",
                "ec2-23-21-9-103.compute-1.amazonaws.com"]

def start_remote_process(cmd, user, host):
    """Starts a remote process on a remote host"""
    ssh_connect = "ssh %s@%s" % (user, host)
    cmd = ssh_connect + " " + cmd
    os.popen(cmd)

def execute_remote_command(cmd, user, host):
    """Executes a given command on a remote host"""
    ssh_connect = "ssh %s@%s" % (user, host)
    cmd = ssh_connect + " " + cmd
    text = os.popen(cmd).read()
    return text

def get_simulator_process_id(host):
    """Returns PIDs of currently running simulator processes"""
    cmd = "ps ux | grep simulate-source"
    response = execute_remote_command(cmd, source_user, host)
    if len(response) > 0:
        return response.split()[1]
    else:
        return None

def stop_simulator(pid, host):
    print "Stopping simulator on host %s" % host
    cmd = "kill %s" % pid
    response = execute_remote_command(cmd, source_user, host)
    print response

def start_simulator(host):
    print "Starting simulator on host %s" % host
    cmd = "python ./simulator/simulate-source \
            -c simulator/config/default.yaml \
            -n %s -l -e" % host
    response = start_remote_process(cmd, source_user, host)

def main():
    pid = get_simulator_process_id(source_hosts[0])
    if pid is not None:
        stop_simulator(pid, source_hosts[0])
    else:
        start_simulator(source_hosts[0])
    
if __name__ == '__main__':
   main()                   