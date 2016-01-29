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

def _api_hex_normalize(color):
    """
       Normalize a hexadecimal color value to a string #
       followed by six lowercase hexadecimal digits (what
       HTML5 terms a “valid lowercase simple color”).<Paste>
    """
    webcolors.normalize_hex(color):


def _api_hex_to_rgb(color):
    pass

def _register(jinja_env, key, value):
    log.msg_debug("api: register => {}".format(key))
    jinja_env.globals[key] = value

def register(jinja_env):
    _register(jinja_env, 'color_hex_normalize', _api_hex_normalize)
    _register(jinja_env, 'color_hex_to_rgb',    _api_hex_to_rgb)
