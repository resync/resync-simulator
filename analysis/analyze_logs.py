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
        if source_log_file is not None:
            (self.src_msg, self.src_events) = \
                self.parse_log_file(source_log_file)
        if destination_log_file is not None:
            (self.dst_msg, self.dst_events) = \
                self.parse_log_file(destination_log_file)
        self.print_log_overview()
    
    def parse_log_file(self, log_file):
        """Parses log files and returns a dictionary of extracted data"""
        msg = {}
        events = {}
        print "Parsing %s ..." % log_file
        for line in open(log_file, 'r'):
            log_entry = [entry.strip() for entry in line.split("|")]
            log_time = self.parse_datetime(log_entry[0])
            if log_entry[3].find("Event: ") != -1:
                event_dict_string = log_entry[3][len("Event: "):]
                event_dict = ast.literal_eval(event_dict_string)
                events[log_time] = event_dict
            else:
                msg[log_time] = log_entry[3]
        return (msg, events)
    
    def print_log_overview(self):
        """Prints an overview of data extracted from the logfiles"""
        if self.src_msg and self.src_events:
            print "*** Information extract from Source log file:"
            print "\t%d events and %d log messages:" % (len(self.src_events),
                                                        len(self.src_msg))
            print "\tsimulation start: %s" % self.src_simulation_start
            print "\tsimulation end: %s" % self.src_simulation_end
            print "\tsimulation duration: %s" % self.src_simulation_duration
            print "\tno bootstrap events: %d" % len(self.src_bootstrap_events)
            print "\tno simulation events: %d" % len(self.src_simulation_events)
        if self.dst_msg and self.dst_events:
            print "*** Information extract from Destimnation log file:"
            print "\t%d events and %d log messages." % (len(self.dst_events),
                                                        len(self.dst_msg))
            print "\tsimulation start: %s" % self.dst_simulation_start
            print "\tsimulation end: %s" % self.dst_simulation_end
            print "\tsimulation duration: %s" % self.dst_simulation_duration
            
    @property
    def src_simulation_start(self):
        """The source simulation start time"""
        for (log_time, msg) in self.src_msg.items():
            if "Starting simulation" in msg:
                return log_time
        return None
    
    @property
    def src_simulation_end(self):
        """The source simulation end time (= the last recorded vent)"""
        return sorted(self.src_events.keys())[-1]

    @property
    def src_simulation_duration(self):
        """Duration of the simulation at the source"""
        return self.src_simulation_end-self.src_simulation_start

    @property
    def src_bootstrap_events(self):
        """The events that happended before the simulation start"""
        return self.events_before(self.src_events, self.src_simulation_start)

    @property
    def src_simulation_events(self):
        """The events that happened during the simulation"""
        return self.events_after(self.src_events, self.src_simulation_start)
    
    def events_before(self, events, time):
        """All events in events that happened before a certain time"""
        return [event for (logtime, event) in events.items()
                      if logtime < time]
    
    def events_after(self, events, time):
        """All events in events that happened before a certain time"""
        return [event for (logtime, event) in events.items()
                      if logtime > time]
    
    @property
    def dst_simulation_start(self):
        """Destination simulation start time (=1st completed sync)"""
        for log_time in sorted(self.dst_msg):
            if "Completed sync" in self.dst_msg[log_time]:
                return log_time
        return None
    
    @property
    def dst_simulation_end(self):
        """Destination simulation end time (=last started sync)"""
        for log_time in sorted(self.dst_msg, reverse=True):
            if "Starting sync" in self.dst_msg[log_time]:
                return log_time
        return None
    
    @property
    def dst_simulation_duration(self):
        """Duration of the simulation at the Destination"""
        return self.dst_simulation_end-self.dst_simulation_start
    
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
        try:
            dt = datetime.datetime.strptime(utc_datetime_string, fmt)
        except ValueError:
            # try without decimal seconds
            fmt = '%Y-%m-%dT%H:%M:%SZ'
            dt = datetime.datetime.strptime(utc_datetime_string, fmt)
        return(dt)

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
    # analyzer.compute_sync_accuracy()

if __name__ == '__main__':
    main()
