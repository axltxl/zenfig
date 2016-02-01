# -*- coding: utf-8 -*-

"""
zenfig.kit
~~~~~~~~

Kit interface

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os
import re

from . import log
from . import util

from .kits import git, local

######################
# List of kit backends
# a.k.a. drivers
######################
_kit_drivers = {
    "git": git,
    "local": local
}

# kit driver to be used
_kit_driver = None

def _set_driver(driver):
    global _kit_driver
    _kit_driver = _kit_drivers[driver]
    log.msg_debug("Using kit driver: {}".format(driver))

def init(kit_name=None, *, driver=None):
    """
    Initialize kit interface

    This will deduct what type of kit this is dealing with,
    it will load the appropiate interface based on kit_name.

    :param kit_name: Name of the kit to be loaded
    :param driver: Kit driver to be used to load kit_name
    """
    # if driver has not been enforced
    # then, deduct proper driver for kit_name
    if driver is None:
        # test whether kit_name is a absolute directory
        if re.match("^\/", kit_name):
            log.msg_debug("Using '{}' as absolute directory".format(kit_name))
            _set_driver("local")
        # test whether kit_name is a relative directory
        elif os.path.isdir(os.path.join(os.getcwd(), kit_name)):
            log.msg_debug("Using '{}' as relative directory".format(kit_name))
            _set_driver("local")
        # test whether kit_name is a git URL
        else:
            _set_driver("git")
    else:
        _set_driver("local")
        log.msg_debug("Kit driver '{}' has been imposed!".format(driver))

    # Initiate kit driver
    _kit_driver.init()

def get_var_dir(kit_name):
    """
    Get variable location from kit_name

    :param kit_name: Kit name
    :returns:
        Full path to the variables directory of the kit.
        None is returned on whether kit_name has an invalid location.
    """

    if _kit_driver.kit_exists(kit_name):
        return _kit_driver.get_var_dir(kit_name)
    return None

def get_template_dir(kit_name):
    """
    Get template location from kit_name

    :param kit_name: Kit name
    :returns:
        Full path to the templates directory of the kit.
        None is returned on whether kit_name has an invalid location.
    """

    if _kit_driver.kit_exists(kit_name):
        return _kit_driver.get_template_dir(kit_name)
    return None
