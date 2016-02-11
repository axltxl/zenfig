
"""
zenfig.kits.local
~~~~~~~~

Local file system kit provider

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os

from . import Kit

from ..util import autolog


@autolog
def get_kit(kit_name):
    """Initialise kit provider"""

    return Kit(kit_name, root_dir=os.path.abspath(kit_name))
