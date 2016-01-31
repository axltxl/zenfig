# -*- coding: utf-8 -*-

"""
zenfig.util
~~~~~~~~

Utilities

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""
import os

def get_xdg_data_home():
    """Get XDG_DATA_HOME"""

    # XDG_DATA_HOME/zenfig/templates is inside
    # the template search path
    xdg_data_home = os.getenv('XDG_DATA_HOME')
    if xdg_data_home is None:
        xdg_data_home = "{}/.local/share".format(os.getenv("HOME"))
    return xdg_data_home

