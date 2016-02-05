# -*- coding: utf-8 -*-

"""
zenfig.api
~~~~~~~~

A bunch of utilities used by templates

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import re
import jinja2

from functools import wraps

from .. import log
from ..util import autolog

# all API entries are in here
_api_globals = {}
_api_filters = {}

def apientry(api_func):
    """
    Common routines for all API entries

    :param api_func: API function to be wrapped up
    :returns: whatever api_func returns, on exception, it returns None
    """
    @wraps(api_func)
    def _wrapper(*args, **kwargs):
        try:
            return api_func(*args, **kwargs)
        except Exception as exc:
            log.msg_warn(exc)
            return None
    return _wrapper

@autolog
def _register_global(name, func):
    _api_globals[name] = func

@autolog
def _register_filter(name, func):
    _api_filters[name] = func

@autolog
def get_globals():
    """Get all globals"""
    return _api_globals

@autolog
def get_filters():
    """Get all filters"""
    return _api_filters

####################################################
# Bring all API functions so they are all registered
# in no time
####################################################
from . import color
