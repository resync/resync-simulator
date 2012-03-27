#!/usr/bin/env python

import optparse
import web

# web stuff -> TODO: put into container / module or class

render = web.template.render('templates/')

urls = (
  '/resources/(\d*)', 'index'
)

class index:
    def GET(self, name):
        return render.index(name)

# change simulator


        


def main():
    p = optparse.OptionParser(usage="%prog [options]", version="%prog 0.1")
    p.add_option('--resources', '-r', default=1000,
                 type = "int", help="the number of seed resources")
    p.add_option('--frequency', '-f', default = 1,
                 type = "int",
                 help="the number of changes to be simulated per second")
    event_types = ['create', 'delete', 'update', 'all']
    p.add_option('--event_type', '-t', choices = event_types,
                 help="the change event types to be fired (%s)" % event_types)
    options, arguments = p.parse_args()
    
    print options.event_type
    
    #print 'Starting Web Server'
    #app = web.application(urls, globals())
    #app.run()
    

if __name__ == '__main__':
    main()

