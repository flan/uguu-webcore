import json
import uuid

import tornado.web

from application import (
 MAKO_TEMPLATES,
 COOKIE_DOMAINS,
 MEMCACHE_POOLS,
)
    
class Session(dict):
    _namespace = None
    _id = None
    _data = False
    _saved = False
    
    def __init__(self, session_id, namespace):
        dict.__init__(self)
        self._namespace = namespace
        self._id = session_id
        
    def __getitem__(self, key):
        self.load()
        return dict.__getitem__(self, key)
        
    def __setitem__(self, key, value):
        self.load()
        return dict.__setitem__(self, key, value)
        
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
            
    def load(self):
        if not self._data:
            self.clear()
            with MEMCACHE_POOLS[self._namespace].reserve() as mc:
                content = mc.get(self._id)
                if content:
                    self.update(json.loads(content))
            self._data = True
                    
    def discard(self):
        self._data = False
        
    def save(self):
        if self._data:
            with MEMCACHE_POOLS[self._namespace].reserve() as mc:
                mc.set(self._id, json.dumps(self, separators=(',', ':')))
                
class ServiceHandler(tornado.web.RequestHandler):
    """
    Provides common logic, including sessions.
    """
    _NAMESPACE = None
    _SESSION_ID = None
    
    _session = None
    
    def prepare(self):
        self._SESSION_ID = self.get_cookie('session-id') or uuid.uuid4().hex
        self.set_cookie('session-id', self._SESSION_ID, domain=COOKIE_DOMAINS[self._NAMESPACE])        
        self.content_type = 'text/plain'
        self._session = Session(self._SESSION_ID, self._NAMESPACE)
        
class JsonHandler(ServiceHandler):
    """
    Provides structured JSON I/O processing.
    """
    def prepare(self):
        ServiceHandler.prepare(self)
        self.content_type = 'application/json'
        
class PageHandler(ServiceHandler):
    """
    Adds Mako-based rendering logic.
    """
    _TEMPLATE = '__null'
    
    def _render(self, template, kwargs):
        return MAKO_TEMPLATES[self._NAMESPACE].get_template(template + '.mako').render(**kwargs)
        
    def prepare(self):
        ServiceHandler.prepare(self)
        self.content_type = 'text/html'
        
    def _display(self, **kwargs):
        local = dict((k[2:], getattr(self, k)) for k in dir(self) if k.startswith(('v_', 'm_')))
        local.update(kwargs)
        self.write(MAKO_TEMPLATES[self._NAMESPACE].get_template(self._TEMPLATE + '.mako').render(session=self._session, **local))
        
