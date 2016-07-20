# -*- coding: utf-8 -*-

"""
zenfig.api.utils
~~~~~~~~

General utilities

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import jinja2

from . import _register_filter
from . import apientry

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

###################################
# Register all functions on the API
###################################
_register_filter('bool2str', bool2str)
