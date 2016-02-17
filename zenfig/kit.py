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
from .util import autolog
from .kits import git, local, KitException
from .kits.git import GitRepoKit


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

    # Local kit version requested by the user
    kit_version = None

    # if provider has not been enforced
    # then, deduct proper provider for kit_name
    if provider is None:

        # test whether kit_name is a absolute directory
        if re.match("^\/", kit_name):
            log.msg_debug("Using '{}' as absolute directory".format(kit_name))
            provider = local

        # test whether kit_name is a relative directory
        elif os.path.isdir(os.path.join(os.getcwd(), kit_name)):
            log.msg_debug("Using '{}' as relative directory".format(kit_name))
            provider = local

        # see whether kit_name matches git kit criteria
        elif re.match(GitRepoKit.RE_GIT_REPO_SHORT, kit_name) \
        or re.match(GitRepoKit.RE_GIT_REPO_URL, kit_name):
            if re.match('.*==.*', kit_name):
                kit_name, kit_version = kit_name.split('==')
            provider = git

        # when everything else fails ...
        else:
            raise KitException("'{}' is not a valid provider".format(provider))
    else:
        provider = local
        log.msg_debug("Kit provider '{}' has been imposed!".format(provider))

    # Get a Kit instance from the provider
    return provider.get_kit(kit_name, kit_version)
