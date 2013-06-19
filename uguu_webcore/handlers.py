import json
import uuid

import pylibmc

import mako.lookup
import tornado.web

_MAKO_TEMPLATES = None
def init(content_path):
    global _MAKO_TEMPLATES
    _MAKO_TEMPLATES = mako.lookup.TemplateLookup(
     directories=[content_path],
     module_directory='/tmp/ynga.me/mako_modules',
     strict_undefined=True,
    )
    
def _render(template, kwargs):
    global _MAKO_TEMPLATES
    return _MAKO_TEMPLATES.get_template(template + '.mako').render(**kwargs)
    
class Session(object):
    _id = None
    _data = None
    
    def __init__(self, session_id):
        self._id = session_id
        
    def load(self):
        if self._data is None:
            self._data = True #Load it from memcache
            
    def discard(self):
        if self._data is not None:
            self._data = None
            
    def save(self):
        if self._data is not None:
            #Write it to memcache
            self._data = None
            
class ServiceHandler(tornado.web.RequestHandler):
    """
    Provides common logic, including sessions.
    """
    _AUTO_SAVE_SESSION = False
    _AUTO_SAVE_SESSION_ON_ERROR = False
    _SESSION_ID = None
    
    _session = None
    
    def prepare(self):
        self._SESSION_ID = self.get_cookie('session-id') or uuid.uuid4().hex
        self.set_cookie('session-id', self._SESSION_ID, domain=)

RequestHandler.set_cookie(name, value, domain=None, expires=None, path='/', expires_days=None, **kwargs)
        
        self.content_type = 'text/plain'
        self._session = Session(self._SESSION_ID) #Prepare a session reference object, but do not request data until needed
            
    def on_finish(self):
        if self._AUTO_SAVE_SESSION:
            self._session.save()
            
    #For cookies, use either self.set_cookie or self._set_secure_cookie
    #For sessions, use memcache, which needs to be configurable through a command-line option
    
    #Expose get/set mechanisms for the session, making cookies transparent.
    
class JsonHandler(ServiceHandler):
    """
    Provides structured JSON I/O processing.
    """
    def prepare(self):
        YngaServiceHandler.prepare(self)
        self.content_type = 'application/json'
        
class PageHandler(ServiceHandler):
    """
    Adds Mako-based rendering logic.
    """
    _TEMPLATE = '__null'
    
    def prepare(self):
        YngaServiceHandler.prepare(self)
        self.content_type = 'text/html'
        
    def get(self, *args, **kwargs):
        self.write(_render(self._TEMPLATE, {}))
        
    def post(self, *args, **kwargs):
        self.get()
        
class TemplatePageHandler(PageHandler):
    """
    Adds generic header/footer formatting, allowing for minimal templates.
    """
    def get(self, *args, **kwargs):
        self.write(_render('header', {}))
        self.write(_render(self._TEMPLATE, {}))
        self.write(_render('footer', {}))
        
