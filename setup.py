#!/usr/bin/env python
"""
Deployment script for uguu-webcore.
"""
from distutils.core import setup

from uguu_webcore import VERSION

setup(
 name = 'uguu-webcore',
 version = VERSION,
 description = "A minimal, Tornado/Mako/Memcache-based web framework",
 author = 'Neil Tallim',
 author_email = 'flan@uguu.ca',
 license = 'GPLv3',
 url = 'https://github.com/flan/uguu-webcore',
 packages = [
  'uguu_webcore',
 ],
)

