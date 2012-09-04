#!/usr/bin/env python
# encoding: utf-8
"""
analyze_logs.py: Analyses log files and extracts measures into CSV files

"""

import argparse
import sys
import re
import ast
import datetime
import dateutil.parser

class LogAnalyzer(object):
    
    def __init__(self, source_log_file, destination_log_file):
        self.src_bootstrap_start = None
        self.src_bootstrap_events = []
        self.src_simulation_start = None
        self.src_change_events = []
        self.src_simulation_end = None
        if source_log_file is not None:
            self.parse_log_file(source_log_file)
        if destination_log_file is not None:
            "Doing nothing at the moment"
    
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
                event_dt = self.parse_datetime(event_dict['lastmod'])
                event_dict['lastmod_dt'] = event_dt
                events.append(event_dict)
        self.src_change_events = events
        self.src_simulation_end = self.src_change_events[-1]['lastmod']
        print "- Source Bootstrap time: %s" % self.src_bootstrap_start
        print "- Parsed %d bootstrap events" % (len(self.src_bootstrap_events))
        print "- Source Simulation start time: %s" % self.src_simulation_start
        print "- Parsed %d simulated events" % (len(self.src_change_events))
        print "- Source Simulation end time: %s" % self.src_simulation_end
        self.duration = self.parse_datetime(self.src_simulation_end) - \
                        self.parse_datetime(self.src_simulation_start)
        print "- Total Simulation duration: %s" % self.duration
                    
    def compute_sync_accuracy(self, intervals=10):
        """Outputs synchronization accuracy at given intervals"""
        interval_duration = self.duration.seconds / (intervals)
        start_datetime = self.parse_datetime(self.src_simulation_start)
        print "Time\t\t\t\tResources\te_created\te_updated\te_deleted"
        for interval in range(intervals+1):
            delta = interval_duration * interval
            time = start_datetime + datetime.timedelta(0, delta)
            src_state = self.compute_source_state(time)
            dst_state = self.compute_source_state(time) #TODO: impl dest state
            # accuracy = set(src_state['resources'].values()) - \
            #            set(dst_state['resources'].values())
            # print accuracy
            print "%s\t%d\t\t%d\t\t%d\t\t%d" % (time, 
                                    len(src_state['resources']),
                                    src_state['e_created'],
                                    src_state['e_updated'],
                                    src_state['e_deleted'])
    
    def compute_source_state(self, time):
        "Compute the resource state at a given point in time"
        resources={}
        for event in self.src_bootstrap_events: # bootstrap events
            self.apply_event(resources, event)
        events = [event for event in self.src_change_events # change events
                            if event['lastmod_dt']<=time]
        for event in sorted(events, key=lambda event: event['lastmod_dt']):
            self.apply_event(resources, event)
        e_created = [event for event in events
                        if event['changetype']=='CREATED']
        e_updated = [event for event in events
                        if event['changetype']=='UPDATED']
        e_deleted = [event for event in events
                        if event['changetype']=='DELETED']
        state = {'resources': resources,
                 'e_created': len(e_created),
                 'e_updated': len(e_updated),
                 'e_deleted': len(e_deleted)}
        return state

    # PRIVATE STUFF
    def parse_datetime(self, utc_datetime_string):
        """Parse a datetime object from a UTC string"""
        fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
        return datetime.datetime.strptime(utc_datetime_string, fmt)
    
    def apply_event(self, resources, event):
        """Applies a given event to a given list of resources"""
        changetype = event['changetype']
        resource = {'uri': event['uri'],
                    'md5': event['md5'],
                    'size': event['size'],
                    'lastmod': event['lastmod'],
                    'dt': event['lastmod_dt']}
        if changetype == "CREATED":
            resources[resource['uri']] = resource
        elif changetype == "UPDATED":
            del resources[resource['uri']]
            resources[resource['uri']] = resource
        elif changetype == "DELETED":
            del resources[resource['uri']]
        else:
            print "WARNING - Unknow changetype in event %s" % event
        return resources

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