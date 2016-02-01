
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

from . import __kit_isvalid

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
    return __kit_isvalid(_get_kit_dir(kit_name))

########################
# kit interface routines
########################
def get_template_dir(kit_name):
    return "{}/templates".format(_get_kit_dir(kit_name))

def get_var_dir(kit_name):
    return "{}/defaults".format(_get_kit_dir(kit_name))

