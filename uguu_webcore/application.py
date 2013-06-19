import hashlib

import mako.lookup
import pylibmc
import tornado.autoreload
import tornado.ioloop
import tornado.web

MAKO_TEMPLATES = {}
COOKIE_DOMAINS = {}
MEMCACHE_POOLS = {}

class Application(object):
    def __init__(self, routes, templates, cookie_domain, interface='127.0.0.1', port=8888, memcache_servers=('127.0.0.1',), memcache_pool_size=25, autoreload=True, name=None):
        self._autoreload = autoreload
        self._interface = interface
        self._port = port
        self._application = tornado.web.Application(routes)
        
        MAKO_TEMPLATES[name] = mako.lookup.TemplateLookup(
         directories=[templates],
         module_directory='/tmp/uguu-webcore/' + hashlib.md5(name or '').hexdigest() + '/mako_modules',
         strict_undefined=True,
        )
        COOKIE_DOMAINS[name] = cookie_domain
        MEMCACHE_POOLS[name] = memcache_pool = pylibmc.ClientPool()
        memcache_pool.fill(pylibmc.Client(memcache_servers, binary=True, behaviors={"tcp_nodelay": True, "ketama": True}), memcache_pool_size)
        
    def start(self):
        if self._autoreload:
            tornado.autoreload.start()
        self._application.listen(self._port, self._interface)
        tornado.ioloop.IOLoop.instance().start()
        
