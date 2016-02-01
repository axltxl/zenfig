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
# a.k.a. providers
######################
_kit_providers = {
    "git": git,
    "local": local
}

# kit provider to be used
_kit_provider = None

def _set_provider(provider):
    global _kit_provider
    _kit_provider = _kit_providers[provider]
    log.msg_debug("Using kit provider: {}".format(provider))

def init(kit_name=None, *, provider=None):
    """
    Initialize kit interface

    This will deduct what type of kit this is dealing with,
    it will load the appropiate interface based on kit_name.

    :param kit_name: Name of the kit to be loaded
    :param provider: Kit provider to be used to load kit_name
    """
    # if provider has not been enforced
    # then, deduct proper provider for kit_name
    if provider is None:
        # test whether kit_name is a absolute directory
        if re.match("^\/", kit_name):
            log.msg_debug("Using '{}' as absolute directory".format(kit_name))
            _set_provider("local")
        # test whether kit_name is a relative directory
        elif os.path.isdir(os.path.join(os.getcwd(), kit_name)):
            log.msg_debug("Using '{}' as relative directory".format(kit_name))
            _set_provider("local")
        # test whether kit_name is a git URL
        else:
            _set_provider("git")
    else:
        _set_provider("local")
        log.msg_debug("Kit provider '{}' has been imposed!".format(provider))

    # Initiate kit provider
    _kit_provider.init()

def get_var_dir(kit_name):
    """
    Get variable location from kit_name

    :param kit_name: Kit name
    :returns:
        Full path to the variables directory of the kit.
        None is returned on whether kit_name has an invalid location.
    """

    if _kit_provider.kit_exists(kit_name):
        return _kit_provider.get_var_dir(kit_name)
    return None

def get_template_dir(kit_name):
    """
    Get template location from kit_name

    :param kit_name: Kit name
    :returns:
        Full path to the templates directory of the kit.
        None is returned on whether kit_name has an invalid location.
    """

    if _kit_provider.kit_exists(kit_name):
        return _kit_provider.get_template_dir(kit_name)
    return None
