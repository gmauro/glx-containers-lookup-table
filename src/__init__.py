# Galaxy containers lookup table builder


import os

from appdirs import *

__all__ = ['__appname__', '__version__', 'log_file']

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(os.path.dirname(here), 'src', 'APPNAME')) as app_file:
    __appname__ = app_file.read().strip()

with open(os.path.join(os.path.dirname(here), 'src', 'VERSION')) as version_file:
    __version__ = version_file.read().strip()


log_file = user_log_dir(__appname__)
