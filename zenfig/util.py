# -*- coding: utf-8 -*-

"""
zenfig.util
~~~~~~~~

Utilities

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""
import os

from . import __name__ as pkg_name

def get_xdg_cache_home():
    """Get XDG_CACHE_HOME"""

    # XDG_CACHE_HOME/zenfig/templates is inside
    # the template search path
    xdg_cache_home = os.getenv('XDG_CACHE_HOME')
    if xdg_cache_home is None:
        xdg_cache_home = "{}/.cache/{}".format(os.getenv("HOME"), pkg_name)
    return xdg_cache_home

def get_xdg_data_home():
    """Get XDG_DATA_HOME"""

    # XDG_DATA_HOME/zenfig/templates is inside
    # the template search path
    xdg_data_home = os.getenv('XDG_DATA_HOME')
    if xdg_data_home is None:
        xdg_data_home = "{}/.local/share/{}".format(os.getenv("HOME"), pkg_name)
    return xdg_data_home

