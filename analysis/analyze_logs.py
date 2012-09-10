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

### Utility functions

def parse_datetime(utc_datetime_string):
     """Parse a datetime object from a UTC string"""
     fmt = '%Y-%m-%dT%H:%M:%S.%fZ'
     try:
         dt = datetime.datetime.strptime(utc_datetime_string, fmt)
     except ValueError:
         # try without decimal seconds
         fmt = '%Y-%m-%dT%H:%M:%SZ'
         dt = datetime.datetime.strptime(utc_datetime_string, fmt)
     return(dt)

def datetime_as_seconds(dt):
    return(dt.seconds + dt.microseconds/1000000.0)


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
    
    def __init__(self, source_log_file, destination_log_file, verbose=False):
        self.verbose = verbose
        self.simulation_start = None
        self.simulation_end = None
        if source_log_file is not None:
            (self.src_msg, self.src_events) = \
                self.parse_log_file(source_log_file)
        if destination_log_file is not None:
            (self.dst_msg, self.dst_events) = \
                self.parse_log_file(destination_log_file)
        self.print_log_overview()
        #
        self.src_state = None
        self.src_prev_time = None
        self.dst_state = None
        self.dst_prev_time = None
    
    def parse_log_file(self, log_file):
        """Parses log files and returns a dictionary of extracted data"""
        msg = {}
        events = {}
        print "Parsing %s ..." % log_file
        for line in open(log_file, 'r'):
            log_entry = [entry.strip() for entry in line.split("|")]
            log_time = parse_datetime(log_entry[0])
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
        try:
             return self.src_simulation_end-self.src_simulation_start
        except TypeError:
             return None

    @property
    def src_bootstrap_events(self):
        """The events that happended before the simulation start"""
        try:
             return self.events_before(self.src_events, self.src_simulation_start)
        except TypeError:
             return []

    @property
    def src_simulation_events(self):
        """The events that happened during the simulation"""
        try:
             return self.events_after(self.src_events, self.src_simulation_start)
        except TypeError:
             return []

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
        """Duration of the simulation for destination"""
        if (self.dst_simulation_end is None or
            self.dst_simulation_start is None):
             return None
        return self.dst_simulation_end-self.dst_simulation_start
    
    
    ### Simulation start, end, duration from instance vars 

    @property
    def simulation_duration(self):
        """Duration of the simulation"""
        return self.simulation_end-self.simulation_start
    
    @property
    def simulation_duration_as_seconds(self):
        """Duration of the simulation at the Destination

        Returns a floating point number of seconds
        """
        return datetime_as_seconds(self.simulation_duration)

    ### Extraction of events from a dict indexed by log_time

    def events_before(self, events, time):
        """All events in events that happened before a certain time"""
        relevant_logs = [log_time for log_time in events
                                  if log_time < time]
        return dict((logtime, events[logtime]) for logtime in relevant_logs)
    
    def events_after(self, events, time):
        """All events in events that happened after a certain time"""
        relevant_logs = [log_time for log_time in events
                                  if log_time > time]
        return dict((logtime, events[logtime]) for logtime in relevant_logs)

    def events_between(self, events, start, end):
        """All events in events that happened after start and up to end time

        Interval exclusive at start and inclusive at end: start < t <= end
        """
        relevant_logs = [log_time for log_time in events
                                  if start < log_time and log_time <= end ]
        return dict((logtime, events[logtime]) for logtime in relevant_logs)

    def compute_sync_accuracy_by_intervals(self, intervals=10):
        """Output synchronization accuracy at given intervals and overall

        The overall accuracy is calculated as the mean of the accuracy over
        all intevals.
        """
        interval_duration = self.simulation_duration_as_seconds / intervals
        if (self.verbose):
            print "\nTime\tsrc_res\tdst_res\tin_sync"
        overall_accuracy = 0.0
        num = 0 
        for interval in range(intervals+1):
            delta = interval_duration * interval
            time = self.simulation_start + datetime.timedelta(0, delta)
            accuracy = self.compute_accuracy_at(time)
            overall_accuracy += accuracy
            num += 1
        overall_accuracy /= num
        print "# Overall accuracy by intervals = %f" % (overall_accuracy)

    def compute_sync_accuracy_by_events(self):
        """Output synchronization accuracy at each event and overall

        Calculation is done by averaging over the entire time of the simulation.
        The average is calculated by taking the accuracy at each event (in either
        source or destincation log) and then saying that that is the accuracy
        until the next event. The time between events is thus a weighting for
        each measure.
        """
        if (self.verbose):
            print "\nTime\tsrc_res\tdst_res\tin_sync"
        # Get merged list of event times from source and destination. Since 
        # these are the only points of change we will get a complete picture 
        # by calculating accuracy at each event. However, we also add in the 
        # start and end times of the simulation period to avoid biasing the 
        # outcome by considering only the active period.
        times = set()
        for log_time in self.events_between(self.src_events,
                                            self.simulation_start,
                                            self.simulation_end).keys():
            times.add(log_time)
        for log_time in self.events_between(self.dst_events,
                                            self.simulation_start,
                                            self.simulation_end).keys():
            times.add(log_time)
        times.add(self.simulation_start)
        times.add(self.simulation_end)
        # Now do calc at every time in set, remembering inteval since last
        overall_accuracy = 0.0
        last_accuracy = 0.0
        last_time = None
        total_time = 0.0
        for time in sorted(times):
            accuracy = self.compute_accuracy_at(time)
            if (last_time is not None):
                dt = datetime_as_seconds(time-last_time)
                overall_accuracy += last_accuracy * dt
                total_time += dt
            last_accuracy = accuracy
            last_time = time
        overall_accuracy /= total_time
        print "# Overall accuracy by events = %f" % (overall_accuracy)

    def compute_accuracy_at(self, time):
        """Compute accuracy at a point in time

        At a time point the accuracy is calculated as the number of 
        number of resources in sync divided by the mean of the number 
        or resources at the source and destination.

        Stores the resulting state and the time it was calculated at for
        both src and dst so that in the case of requesting a sequence of
        accuracies with timesteps moving forward, only additional events
        since the last call are applied each time.
        """
        self.src_state = self.compute_state(self.src_events, time, 
                                            prev_state=self.src_state,
                                            prev_time=self.src_prev_time)
        self.src_prev_time=time
        src_n = len(self.src_state)
        self.dst_state = self.compute_state(self.dst_events, time,
                                            prev_state=self.dst_state,
                                            prev_time=self.dst_prev_time)
        self.dst_prev_time=time
        dst_n = len(self.dst_state)
        sync_resources = [r for r in self.dst_state
                            if self.src_state.has_key(r) and
                            self.dst_state[r].in_sync_with(self.src_state[r])]
        accuracy = 2.0 * len(sync_resources) / (dst_n + src_n)
        if (self.verbose):
            print "%s\t%d\t\t%d\t\t%f" % (time, src_n, dst_n, accuracy)
        return(accuracy)

    def compute_state(self, events, time, prev_state=None, prev_time=None):
        """Compute the set of resources at a given point in time
        
        If prev_events is given in prev_time<=time then that state is used
        as the starting point and only events for prev_state<t<=time are 
        added in.
        """
        if (prev_state is None or prev_time is None or prev_time>time):
            # start from scratch
            resources={}
            events = self.events_before(events, time)
        elif (prev_time==time):
             return(prev_state)
        else:
            # start from past state (prev_time<time)
            resources = prev_state
            events = self.events_between(events, prev_time, time)
        # run forward adding in events
        for log_time in sorted(events.keys()):
            event = events[log_time]
            resource = Resource(uri=event['uri'], md5=event['md5'],
                                size=event['size'],lastmod=event['lastmod'])
            if event['changetype'] == "CREATED":
                resources[resource.uri] = resource
            elif event['changetype'] == "UPDATED":
                resources[resource.uri] = resource
            elif event['changetype'] == "DELETED":
                del resources[resource.uri]
            else:
                print "WARNING - Unknown changetype in event %s" % event
        return resources

    def compute_latency(self):
        """Outputs synchronization latency for all events

        """
        if (self.verbose):
            print "\nTime\tResource\tLatency (s)\tComment"
        sim_events = self.events_between(self.src_events,
                                         self.simulation_start,
                                         self.simulation_end)
        # ?simeon? is the assumption that no two events ever occur at the same time going to 
        # be an issue? I suspect not (unless we merge things from src and dst)
        num_events = 0;
        total_latency = 0.0;
        num_missed = 0;
        for log_time in sorted(sim_events.keys()):
            # For each src event search forward in dst_events for the 
            # corresponding update
            update_time = self.find_event(sim_events[log_time],
                                          self.dst_events,log_time,self.simulation_end)
            if (update_time is None):
                if (self.verbose):
                    print "%s\t%s\t-\tNo match" % (str(log_time),sim_events[log_time]['uri'])
                num_missed+=1
            else:
                l = datetime_as_seconds(update_time-log_time)
                if (self.verbose):
                    print "%s\t%s\t%f\t%s" % (str(log_time),sim_events[log_time]['uri'],l,'')
                num_events+=1
                total_latency+=l
        if (num_events == 0):
             print "# No events -> can't calculate latency (%d omitted as not found)" % (num_missed)
        else:
             print "# Average latency = %fs (%d events; %d omitted as not found)" % (total_latency/num_events, num_events, num_missed)

    def find_event(self,resource,events,start,end):
        """Find and update to resource with matching metadata in events after start
        and not after end
        """
        tpast = end + datetime.timedelta(0, 1) #after end
        t = tpast
        for log_time in events:
            # need to abstract in_sync comparison, should the events be dicts or
            # Resource objects?
            if (log_time>=start and log_time<=end and log_time<t and
                resource['uri']==events[log_time]['uri'] and
                ( resource['md5']==events[log_time]['md5'] or
                  ( resource['changetype']=='DELETED' and events[log_time]['changetype']=='DELETED')) ):
                t=log_time
        return( None if t==tpast else t )
    
def main():

    # Define simulator options
    parser = argparse.ArgumentParser(
                            description = "ResourceSync Log Analyzer")
    parser.add_argument('--source-log', '-s',
                        help="the source log file")
    parser.add_argument('--destination-log', '-d', 
                        help="the destination log file")
    parser.add_argument('--start',
                        help="start simulation at this time (otherwise take from dst log)")
    parser.add_argument('--end',
                        help="end simulation at this time (otherwise take from dst log)")
    parser.add_argument('--intervals', '-i',
                        help="the number of intervals to test sync at")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="verbose")

    # Parse command line arguments
    args = parser.parse_args()

    analyzer = LogAnalyzer(args.source_log, args.destination_log, verbose = args.verbose)
    # Either take start and end from destination logs, or set explicitly
    if (args.start):
        analyzer.simulation_start = parse_datetime(args.start)        
    else:
        analyzer.simulation_start = analyzer.dst_simulation_start
    if (args.end):
        analyzer.simulation_end = parse_datetime(args.end)        
    else:
        analyzer.simulation_end = analyzer.dst_simulation_end
    print "\nDoing calculations for period %s to %s" % (str(analyzer.simulation_start),
                                                        str(analyzer.simulation_end))
    # Now do that math
    if (args.intervals):
        analyzer.compute_sync_accuracy_by_intervals(intervals=int(args.intervals))
    analyzer.compute_sync_accuracy_by_events()
    analyzer.compute_latency()

if __name__ == '__main__':
    main()
