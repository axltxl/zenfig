
"""
zenfig.kits.local
~~~~~~~~

Local file system kit provider

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os

from .. import log
from .. import util

def _get_kit_dir(kit_name):
    return os.path.abspath(kit_name)

def init():
    """Initialise kit"""
    pass

def kit_isvalid(kit_name):
    """
    Tell whether a kit is existent and valid

    :param kit_name: Kit to be validated
    """
    kit_dir = _get_kit_dir(kit_name)
    if not os.path.isdir(kit_dir):
        return False
    if not os.path.isdir("{}/templates".format(kit_dir)):
        return False
    if not os.path.isdir("{}/defaults".format(kit_dir)):
        return False
    return True

########################
# kit interface routines
########################
def get_template_dir(kit_name):
    return "{}/templates".format(_get_kit_dir(kit_name))

def get_var_dir(kit_name):
    return "{}/defaults".format(_get_kit_dir(kit_name))

