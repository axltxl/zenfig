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
from . import log

from . import __name__ as pkg_name

# Based on: http://stackoverflow.com/questions/10973362/python-logging-function-name-file-name-line-number-using-a-single-file
def autolog(log_func):
    "Automatically log the current function details."
    def _log_wrapper(*args, **kwargs):
        # get the function name
        func = log_func.__name__

        # measure its execution time
        start_time = time()
        r = log_func(*args, **kwargs)
        dt = time() - start_time

        # Dump the message + the name of this function to the log.
        log.msg_debug("{} {:.3f} ms".format(func, dt*1000))

        # return whatever log_func has thrown
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


