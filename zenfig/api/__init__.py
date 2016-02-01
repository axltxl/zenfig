# -*- coding: utf-8 -*-

"""
zenfig.api
~~~~~~~~

A bunch of utilities used by templates

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

from .. import log
from ..util import autolog

# all API entries are in here
_api_map = {}

@autolog
def api_entry(api_func):
    """
    Common routines for all API entries

    :param api_func: API function to be wrapped up
    :returns: whatever api_func returns, on exception, it returns None
    """
    def _wrapper(*args, **kwargs):
        try:
            return api_func(*args, **kwargs)
        except Exception as exc:
            log.msg_warn(exc)
            return None
    return _wrapper

@autolog
def _register(key, value):
    _api_map[key] = value

@autolog
def get_map():
    """Get the whole API functions map"""
    return _api_map

####################################################
# Bring all API functions so they are all registered
# in no time
####################################################
from . import color
