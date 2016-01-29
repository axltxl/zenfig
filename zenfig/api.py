# -*- coding: utf-8 -*-

"""
zenfig.api
~~~~~~~~

API for templates

:copyright: (c) 2015 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

# TODO: you know how to revamp this, give it some time
import webcolors
from . import log


def api_entry(api_func):
    def _wrapper(*args, **kwargs):
        try:
           value =  api_func(*args, **kwargs)
        except:
            return "*INVALID*" #TODO: do something better
        return value
    return _wrapper

@api_entry
def _api_hex_normalize(color):
    """
       Normalize a hexadecimal color value to a string
       followed by six lowercase hexadecimal digits (what
       HTML5 terms a “valid lowercase simple color”).<Paste>
    """
    return webcolors.normalize_hex(color)


@api_entry
def _api_hex_to_rgb(color):
    pass

####################################
# The whole API is contained in here
####################################
_api_map = {
    'color_hex_normalize' : _api_hex_normalize,
    'color_hex_to_rgb' : _api_hex_to_rgb
    }


def _register(jinja_env, api_entry, api_func):
    log.msg_debug("api: register => {}".format(api_entry))
    jinja_env.globals[api_entry] = api_func


def register(jinja_env):
    for api_entry, api_func in _api_map.items():
        _register(jinja_env, api_entry, api_func)
