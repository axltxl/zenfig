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

import yaml

from . import log
from . import util
from .util import autolog
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

class InvalidKitError(BaseException):
    def __init__(self, message):
        super().__init__("{} does not have a valid file system.".format(message))

@autolog
def _set_provider(provider):
    global _kit_provider
    _kit_provider = _kit_providers[provider]
    log.msg_debug("Using kit provider: {}".format(provider))

@autolog
def get_kit(kit_name, *, provider=None):
    """
    Initialize kit interface

    This will deduct what type of kit this is dealing with,
    it will load the appropiate interface based on kit_name.

    :param kit_name: Name of the kit to be loaded
    :param provider: Kit provider to be used to load kit_name
    :returns: a Kit holding all relevant information about kit_name
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

        # see whether kit_name matches git kit criteria
        elif re.match("^[a-zA-Z]+\/[a-zA-Z]+$", kit_name) or \
             re.match("^http:.*\.git$", kit_name):
            _set_provider("git")

        # when everything else fails ...
        else:
            raise InvalidKitError(kit_name)
    else:
        _set_provider("local")
        log.msg_debug("Kit provider '{}' has been imposed!".format(provider))

    # Initiate kit provider
    return _kit_provider.get_kit(kit_name)
