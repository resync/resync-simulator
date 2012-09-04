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
import pprint


class Resource(object):
    __slots__=('uri', 'lastmod', 'size', 'md5')
    """A resource representation
    TODO: we should/could re-use resource.py -> requires package restructuring
    """
    def __init__(self, uri, lastmod=None, size=None, md5=None):
        self.uri=uri
        self.lastmod=lastmod
        self.size=size
        self.md5=md5
    
    def in_sync_with(self, other):
        """True if resource is in sync with other resource"""
        return ((self.uri == other.uri) and (self.md5 == other.md5))
    
    def __str__(self):
        return "[%s|%s|%s|%s]" % (self.uri, self.lastmod, self.size, self.md5)
        
    def __repr__(self):
        return self.__str__()

class LogAnalyzer(object):
    
    def __init__(self, source_log_file, destination_log_file):
        self.src_bootstrap_start = None
        self.src_simulation_start = None
        self.src_simulation_end = None
        self.src_events = []
        if source_log_file is not None:
            self.parse_log_file(source_log_file)
        if destination_log_file is not None:
            "Doing nothing at the moment"
    
    @property
    def simulation_duration(self):
        """Duration of the simulation"""
        return self.src_simulation_end-self.src_simulation_start

    @property
    def src_bootstrap_events(self):
        """The events that happended before the simulation start"""
        return self.events_before(self.src_events, self.src_simulation_start)

    @property
    def src_simulation_events(self):
        """The events that happened during the simulation"""
        return [event for event in self.src_events
                      if event['lastmod_dt'] >= self.src_simulation_start]
    
    def events_before(self, events, time):
        """All events in events that happened before a certain time"""
        return [event for event in events if event['lastmod_dt']<=time]
    
    def parse_log_file(self, log_file):
        """Parses log files and returns a dictionary of extracted data"""
        print "Parsing %s ..." % log_file
        for line in open(log_file, 'r'):
            log_entry = [entry.strip() for entry in line.strip().split("|")]
            if log_entry[3] == "Bootstrapping source...":
                self.src_bootstrap_start = self.parse_datetime(log_entry[0])
            if log_entry[3] == "Starting simulation...":
                self.src_simulation_start = self.parse_datetime(log_entry[0])
            if log_entry[3].find("Event: ") != -1:
                event_dict_string = log_entry[3][len("Event: "):]
                event_dict = ast.literal_eval(log_entry[3][len("Event: "):])
                event_dt = self.parse_datetime(event_dict['lastmod'])
                event_dict['lastmod_dt'] = event_dt
                self.src_events.append(event_dict)
        self.src_simulation_end = self.parse_datetime(
                                        self.src_events[-1]['lastmod'])
        print "- Source Bootstrap time: %s" % self.src_bootstrap_start
        print "- Parsed %d bootstrap events" % (len(self.src_bootstrap_events))
        print "- Source Simulation start time: %s" % self.src_simulation_start
        print "- Parsed %d simulated events" % (len(self.src_events))
        print "- Source Simulation end time: %s" % self.src_simulation_end
        print "- Total Simulation duration: %s" % str(self.simulation_duration)
    
    def compute_sync_accuracy(self, intervals=10):
        """Outputs synchronization accuracy at given intervals"""
        interval_duration = self.simulation_duration.seconds / intervals
        print "Time\t\t\t\tResources\te_created\te_updated\te_deleted\taccuracy"
        for interval in range(intervals+1):
            delta = interval_duration * interval
            time = self.src_simulation_start + datetime.timedelta(0, delta)
            src_state = self.compute_source_state(time)
            src_resources = src_state['resources'] # dict(uri|resource)
            dst_state = self.compute_source_state(time) #TODO: impl dest state
            dst_resources = dst_state['resources'] #dict(uri|resource)
            sync_resources = [r for r in dst_resources
                                if src_resources.has_key(r) and
                                dst_resources[r].in_sync_with(
                                                            src_resources[r])]
            accuracy = len(sync_resources) / len(dst_resources)
            print "%s\t%d\t\t%d\t\t%d\t\t%d\t\t%f" % (time,
                                    len(src_state['resources']),
                                    src_state['e_created'],
                                    src_state['e_updated'],
                                    src_state['e_deleted'],
                                    accuracy)
    
    def compute_source_state(self, time):
        "Compute the set of resources at a given point in time"
        resources={}
        events = self.events_before(self.src_events, time)
        for event in sorted(events, key=lambda event: event['lastmod_dt']):
            resource = Resource(uri=event['uri'], md5=event['md5'],
                                size=event['size'],lastmod=event['lastmod'])
            if event['changetype'] == "CREATED":
                resources[resource.uri] = resource
            elif event['changetype'] == "UPDATED":
                resources[resource.uri] = resource
            elif event['changetype'] == "DELETED":
                del resources[resource.uri]
            else:
                print "WARNING - Unknow changetype in event %s" % event
        
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