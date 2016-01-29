# -*- coding: utf-8 -*-

"""
zenfig.api
~~~~~~~~

API for templates

:copyright: (c) 2015 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

# TODO: you know how to revamp this, give it some time
from . import log

def _api_some_fun():
    pass

def _register(jinja_env, key, value):
    log.msg_debug("api: register => {}".format(key))
    jinja_env.globals[key] = value

def register(jinja_env):
    _register(jinja_env, 'zenfig_some_fun', _api_some_fun)
