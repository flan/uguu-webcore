#!/usr/bin/env python
#import optparse
import os

import tornado.autoreload
import tornado.ioloop
import tornado.web

import web
web.init(
    content_path=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'content'),
)

import content
application = tornado.web.Application(content.ROUTING)

if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("--expiration-time", dest="expiration_time", type="int", default=90, help="The number of seconds before a user's status is invalidated")
    (options, args) = parser.parse_args()
    
    tornado.autoreload.start()
    application.listen(8888, '127.0.0.1')
    tornado.ioloop.IOLoop.instance().start()
