# -*- coding: utf-8 -*-

"""
zenfig.log
~~~~~~~~~~~~~

Nice output

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.
"""


import sys
from clint.textui.colored import white, red, cyan, yellow, green
from clint.textui import puts

# Globals
_stdout = False


def init(*, quiet_stdout=True):
    """
    Initiate the log module

    :param threshold_lvl: messages under this level won't be issued/logged
    :param to_stdout: activate stdout log stream
    """

    # create stout handler
    if not quiet_stdout:
        global _stdout
        _stdout = True


def to_stdout(msg, *, colorf=green, bold=False, quiet=True):
    if not quiet or _stdout:
        print(colorf(msg, bold=bold), file=sys.stderr)



def msg(message, *, bold=False):
    """
    Log a regular message

    :param message: the message to be logged
    """
    to_stdout(" --- {message}".format(message=message), bold=bold)


def msg_warn(message):
    """
    Log a warning message

    :param message: the message to be logged
    """
    to_stdout(" (!) {message}".format(message=message),
              colorf=yellow, bold=True, quiet=False)


def msg_err(message):
    """
    Log an error message

    :param message: the message to be logged
    """
    to_stdout(" !!! {message}".format(message=message),
            colorf=red, bold=True, quiet=False)


def msg_debug(message):
    """
    Log a debug message

    :param message: the message to be logged
    """
    to_stdout(" (*) {message}".format(message=message), colorf=cyan)
