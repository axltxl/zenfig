# -*- coding: utf-8 -*-

"""
zenfig.kits
~~~~~~~~

Some message

:copyright: (c) 2015 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os

from ..util import autolog

@autolog
def __kit_isvalid(kit_dir):
    if not os.path.isdir(kit_dir):
        return False
    if not os.path.isdir("{}/templates".format(kit_dir)):
        return False
    if not os.path.isdir("{}/defaults".format(kit_dir)):
        return False
    return True
