#!/usr/bin/env python
# encoding: utf-8
"""
analyze_logs.py: Analyses log files and extracts measures into CSV files

"""

import argparse
import sys
import re
import ast
import dateutil.parser

class LogAnalyzer(object):
    
    def __init__(self, source_log_file, destination_log_file):
        if source_log_file is not None:
            self.parse_log_file(source_log_file)
        if destination_log_file is not None:
            "Doing nothing at the moment"
        self.src_bootstrap_start = None
        self.src_bootstrap_events = []
        self.src_simulation_start = None
        self.src_change_events = []
        self.src_simulation_end = None
    
    def parse_log_file(self, log_file):
        """Parses log files and returns a dictionary of extracted data"""
        print "Parsing %s ..." % log_file
        simulation_started = False
        events=[]
        for line in open(log_file, 'r'):
            log_entry = [entry.strip() for entry in line.strip().split("|")]
            if log_entry[3] == "Bootstrapping source...":
                simulation_started = False
                self.src_bootstrap_start = log_entry[0]
            if log_entry[3] == "Starting simulation...":
                simulation_started = True
                self.src_bootstrap_events = events
                events = []
                self.src_simulation_start = log_entry[0]
            if log_entry[3].find("Event: ") != -1:
                event_dict = ast.literal_eval(log_entry[3][len("Event: "):])
                events.append(event_dict)
        self.src_change_events = events
        self.src_simulation_end = self.src_change_events[-1]['lastmod']
        print "- Source Bootstrap time: %s" % self.src_bootstrap_start
        print "- Parsed %d bootstrap events" % (len(self.src_bootstrap_events))
        print "- Source Simulation start time: %s" % self.src_simulation_start
        print "- Parsed %d simulated events" % (len(self.src_change_events))
        print "- Source Simulation end time: %s" % self.src_simulation_end        
                    
    def get_source_state(self, time):
        """Computes a resource list representing the source state at time t"""
    
    def compute_sync_accuracy(self):
        """Outputs synchronization accuracy at given intervals"""
        pass
        

def main():

    # Define simulator options
    parser = argparse.ArgumentParser(
                            description = "ResourceSync Log Analyzer")
    parser.add_argument('--source-log', '-s',
                                help="the source log file")
    parser.add_argument('--destination-log', '-d', 
                                help="the destination log file")

    # Parse command line arguments
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    analyzer = LogAnalyzer(args.source_log, args.destination_log)
    analyzer.compute_sync_accuracy()

if __name__ == '__main__':
    main()