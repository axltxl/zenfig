# -*- coding: utf-8 -*-

"""
zenfig.api.utils
~~~~~~~~

General utilities

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import jinja2

from . import _register_filter, _register_global
from . import apientry

from .. import log
from ..util import autolog, memoize

@autolog
@memoize
@apientry
def bool2str(value):
    """
    Get string representation of a boolean

    :param value: Value to be converted to string
    """
    if bool(value):
        return 'true'
    return 'false'

#######################################
# Log messages for zenfig templates! :)
#######################################
@apientry
def log_msg(msg):
    """Log a regular message"""

    log.msg("*** {}".format(msg))

@apientry
def log_msg_warn(msg):
    """Log a regular message"""

    log.msg_warn("*** {}".format(msg))

@apientry
def log_msg_err(msg):
    """Log a regular message"""

    log.msg_err("*** {}".format(msg))

@apientry
def log_msg_debug(msg):
    """Log a regular message"""

    log.msg_err("*** {}".format(msg))

###################################
# Register all functions on the API
###################################

_register_global('log_msg', log_msg)
_register_global('log_msg_warn', log_msg_warn)
_register_global('log_msg_err', log_msg_err)
_register_global('log_msg_debug', log_msg_debug)
_register_filter('bool2str', bool2str)
