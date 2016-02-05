# -*- coding: utf-8 -*-

"""
zenfig.util
~~~~~~~~

Utilities

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""
import os
import inspect

from functools import wraps
from time import time

from . import log
from . import __name__ as pkg_name

def memoize(func):
    """
    A simple memcache decorator
    """
    # Cache as dict, all entries go in here
    cache = {}

    # Wrapper function
    @wraps(func)
    def _wrapper(key, *args, **kwargs):
        if isinstance(key, str):
            if key in cache:
                return cache[key]
            cache[key] = func(key, *args, **kwargs)
            return cache[key]
        return func(key, *args, **kwargs)

    # give that wrapper
    return _wrapper

# Based on: http://stackoverflow.com/questions/10973362/python-logging-function-name-file-name-line-number-using-a-single-file
def autolog(func):
    """
    Decorator for automatically log the current function details.
    """

    # Wrapper function
    @wraps(func)
    def _log_wrapper(*args, **kwargs):
        # measure its execution time
        start_time = time()
        r = func(*args, **kwargs)
        dt = time() - start_time

        # Dump the message + the name of this function to the log.
        log.msg_debug("{} {:.3f} ms".format(func.__name__, dt*1000))

        # return whatever func has thrown
        return r
    return _log_wrapper

@autolog
def get_xdg_cache_home():
    """Get XDG_CACHE_HOME"""

    # XDG_CACHE_HOME/zenfig/templates is inside
    # the template search path
    xdg_cache_home = os.getenv('XDG_CACHE_HOME')
    if xdg_cache_home is None:
        xdg_cache_home = "{}/.cache/{}".format(os.getenv("HOME"), pkg_name)
    return xdg_cache_home

@autolog
def get_xdg_data_home():
    """Get XDG_DATA_HOME"""

    # XDG_DATA_HOME/zenfig/templates is inside
    # the template search path
    xdg_data_home = os.getenv('XDG_DATA_HOME')
    if xdg_data_home is None:
        xdg_data_home = "{}/.local/share/{}".format(os.getenv("HOME"), pkg_name)
    return xdg_data_home


