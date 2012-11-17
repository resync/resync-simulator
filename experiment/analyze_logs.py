#!/usr/bin/env python
# encoding: utf-8
"""
analyze_logs.py: Analyses log files and extracts measures into CSV files

"""

import os
import argparse
import sys
import re
import ast
import datetime
import dateutil.parser
import pprint
import csv

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
        self.override_start = None
        self.override_end = None
        if source_log_file is not None:
            (self.src_msg, self.src_events, self.src_reads) = \
                self.parse_log_file(source_log_file)
        if destination_log_file is not None:
            (self.dst_msg, self.dst_events, self.dst_reads) = \
                self.parse_log_file(destination_log_file)
        if self.verbose:
            self.print_log_overview()
        self.src_state = None
        self.src_prev_time = None
        self.dst_state = None
        self.dst_prev_time = None
    
    def parse_log_file(self, log_file):
        """Parses log files and returns a dictionary of extracted data"""
        msg = {}
        events = {}
        reads = {}
        if self.verbose:
            print "Parsing %s ..." % log_file
        for line in open(log_file, 'r'):
            log_entry = [entry.strip() for entry in line.split("|")]
            log_time = parse_datetime(log_entry[0])
            if log_entry[3].find("Event: ") != -1:
                event_dict_string = log_entry[3][len("Event: "):]
                event_dict = ast.literal_eval(event_dict_string)
                events[log_time] = event_dict
            else:
                m = re.match( r"Read (\d+) bytes", log_entry[3] )
                if (m is not None):
                    reads[log_time] = int(m.group(1))
                else:
                    msg[log_time] = log_entry[3]
        return (msg, events, reads)
    
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

    # General simulation properties
    
    @property
    def simulation_start(self):
        # Either take start and end from destination logs, or set explicitly
        if (self.override_start):
            return( parse_datetime(self.override_start) )
        return( self.dst_simulation_start )

    @property
    def simulation_end(self):
        if (self.override_end):
            return( parse_datetime(self.override_end) )        
        return( self.dst_simulation_end )
            
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
    
    
    # Source-specific simulation properties
    
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

    # Destination-specific simulation properties
    
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

    def compute_sync_consistency_by_intervals(self, intervals=10):
        """Output synchronization consistency at given intervals and overall

        The overall consistency is calculated as the mean of the consistency over
        all intevals.
        """
        interval_duration = self.simulation_duration_as_seconds / intervals
        if (self.verbose):
            print "\nTime                        \tsrc_res\tdst_res\tin_sync"
        overall_consistency = 0.0
        num = 0 
        for interval in range(intervals+1):
            delta = interval_duration * interval
            time = self.simulation_start + datetime.timedelta(0, delta)
            consistency = self.compute_consistency_at(time)
            overall_consistency += consistency
            num += 1
        overall_consistency /= num
        if self.verbose:
            print "# Overall consistency by intervals = %f" % (overall_consistency)

    def compute_sync_consistency_by_events(self):
        """Output synchronization consistency at each event and overall

        Calculation is done by averaging over the entire time of the simulation.
        The average is calculated by taking the consistency at each event (in either
        source or destincation log) and then saying that that is the consistency
        until the next event. The time between events is thus a weighting for
        each measure.
        """
        if (self.verbose):
            print "\nTime                        \tsrc_res\tdst_res\tin_sync"
        # Get merged list of event times from source and destination. Since 
        # these are the only points of change we will get a complete picture 
        # by calculating consistency at each event. However, we also add in the 
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
        overall_consistency = 0.0
        last_consistency = 0.0
        last_time = None
        total_time = 0.0
        for time in sorted(times):
            consistency = self.compute_consistency_at(time)
            if (last_time is not None):
                dt = datetime_as_seconds(time-last_time)
                overall_consistency += last_consistency * dt
                total_time += dt
            last_consistency = consistency
            last_time = time
        overall_consistency /= total_time
        if self.verbose:
            print "# Overall consistency by events = %f" % (overall_consistency)
        return overall_consistency

    def compute_consistency_at(self, time):
        """Compute consistency at a point in time

        At a time point the consistency is calculated as the number of 
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
        consistency = 2.0 * len(sync_resources) / (dst_n + src_n)
        if (self.verbose):
            print "%s\t%d\t\t%d\t\t%f" % (time, src_n, dst_n, consistency)
        return(consistency)

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
            print "\nTime                        \tResource\tLatency (s)\tComment"
        sim_events = self.events_between(self.src_events,
                                         self.simulation_start,
                                         self.simulation_end)
        # Here we assume that no two events ever occur at the same
        # time. Given the high resolution of timestamps this cannot
        # be an issue (unless we merge things from src and dst)
        num_events = 0;
        total_latency = 0.0;
        num_missed = 0;
        for log_time in sorted(sim_events.keys()):
            # For each src event search forward in dst_events for the 
            # corresponding update
            update_time = self.find_event(sim_events[log_time],
                                          self.dst_events,log_time,self.dst_simulation_end)
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
             if self.verbose:
                 print "# No events -> can't calculate latency (%d omitted as not found)" % (num_missed)
             return None
        else:
             avg_latency = total_latency/num_events
             if self.verbose:
                 print "# Average latency = %fs (%d events; %d omitted as not found)" % (avg_latency, num_events, num_missed)
             return avg_latency

    def compute_efficiency(self):
        """Outputs a data transfer efficiency based on dst log data

        We define the efficiency as
           e = (useful-bytes / (useful-bytes+extra-bytes))
        where extra-bytes are the bytes in inventories and changesets.
        """
        if (self.verbose):
            print "\nTime                        \tType\tBytes"
        # Calculate useful bytes by adding up all tx in events
        useful_bytes = 0
        sim_events = self.events_between(self.dst_events,
                                         self.dst_simulation_start,
                                         self.dst_simulation_end)
        for log_time in sorted(sim_events.keys()):
            e = sim_events[log_time]
            if ( e['changetype'] == 'UPDATED' or
                 e['changetype'] == 'CREATED'):
                if (self.verbose):
                    print "%s\tuseful\t%d" % (str(log_time), e['size'])
                useful_bytes += e['size']
        # Calculate extra bytes by adding up size of inv/changeset reads
        extra_bytes = 0
        sim_reads = self.events_between(self.dst_reads,
                                        self.dst_simulation_start,
                                        self.dst_simulation_end)
        for log_time in sorted(sim_reads.keys()):
            if (self.verbose):
                print "%s\textra\t%d" % (str(log_time), sim_reads[log_time])
            extra_bytes += sim_reads[log_time]
        if (self.verbose):
            print "Useful bytes: %d, extra bytes: %d" % (useful_bytes,extra_bytes) 
        # Return -1.0 efficiency if we have not data to compute 
        # an efficiency
        if (useful_bytes+extra_bytes)==0:
             return(-1.0)
        return( useful_bytes / float(useful_bytes+extra_bytes) ) 

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
    

def batch_compute_results(log_index_file, verbose = False):
    """Takes a log index file and computes results for src-dst log pairs
    in a batch manner"""

    # we assume that the logs are in the same dir as the index file
    data_dir = os.path.dirname(log_index_file)

    # ...and also write the results file there
    results_file = data_dir + "/results.csv"
    
    with open(results_file, 'wb') as results_csv:
        csv_writer = csv.writer(results_csv, delimiter=';')
        with open(log_index_file, 'rb') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if csv_reader.line_num == 1:
                    row.append("no_events")
                    row.append("consistency")
                    row.append("latency")
                    row.append("efficiency")
                    csv_writer.writerow(row)
                else:
                    exp_id = row[0]
                    print "*** Analyzing logs of experiment %s" % str(exp_id)
                    src_log = data_dir + "/" + row[1]
                    dst_log = data_dir + "/" + row[2]
                    if verbose:
                        print "Source log: %s" % src_log
                        print "Destination log: %s" % dst_log
                    analyzer = LogAnalyzer(src_log, dst_log)
                    if verbose:
                        print "Source simulation start: %s" % analyzer.src_simulation_start
                        print "Destination simulation start: %s" % analyzer.dst_simulation_start
                    # number of events
                    src_events = analyzer.src_simulation_events
                    if src_events is None:
                        no_events = 0
                    else:
                        no_events = len(src_events)
                    if verbose:
                        print "Number of simulation events: %d" % no_events
                    row.append(no_events)
                    # consistency
                    consistency = analyzer.compute_sync_consistency_by_events()
                    if verbose:
                        print "Avg. consistency: %s" % consistency
                    row.append(round(consistency,2))
                    # latency
                    latency = analyzer.compute_latency()
                    if verbose:
                        print "Latency: %s" % latency
                    if latency is None:
                        row.append(-1)
                    else:
                        row.append( "%.2f" % latency )
                    # efficiency
                    efficiency = analyzer.compute_efficiency()
                    if verbose:
                        print "Efficiency: %.5f" % efficiency
                    if efficiency is None:
                        row.append(-1)
                    else:
                        row.append( "%.5f" % efficiency )
                    csv_writer.writerow(row)
    
    print "Wrote results file to %s" % results_file

def main():

    # Define simulator options
    parser = argparse.ArgumentParser(
                            description = "ResourceSync Log Analyzer")
    parser.add_argument('--log-index', '-i',
                        help="an experiment log index file location")
    parser.add_argument('--source-log', '-s',
                        help="the source log file")
    parser.add_argument('--destination-log', '-d', 
                        help="the destination log file")
    parser.add_argument('--start',
                        help="start simulation at this time (otherwise take from dst log)")
    parser.add_argument('--end',
                        help="end simulation at this time (otherwise take from dst log)")
    parser.add_argument('--verbose', '-v', action='store_true',
                        help="verbose")

    # Parse command line arguments
    args = parser.parse_args()

    # Analyze single src/destination log pair
    if args.source_log and args.destination_log:
        analyzer = LogAnalyzer(args.source_log, args.destination_log,
                               verbose = args.verbose)
        print "Doing calculations for period %s to %s" % \
              (str(analyzer.simulation_start), str(analyzer.simulation_end))
        avg_consistency = analyzer.compute_sync_consistency_by_events()
        print "Average consistency: %s" % avg_consistency
        avg_latency = analyzer.compute_latency()
        print "Average latency: %s" % avg_latency
        efficiency = analyzer.compute_efficiency()
        print "Data transfer efficiency: %.6f" % efficiency
    elif args.log_index:
        batch_compute_results(args.log_index, verbose = args.verbose)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
