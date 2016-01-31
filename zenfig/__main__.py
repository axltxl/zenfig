# -*- coding: utf-8 -*-

"""
zenfig.main
~~~~~~~~

Main module

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import sys
import os
import time
import traceback

from docopt import docopt

from docopt import DocoptExit
from zenfig import renderer
from zenfig import log
from zenfig import variables
from zenfig import PKG_URL as pkg_url
from zenfig import __name__ as pkg_name, __version__ as pkg_version

def parse_args(argv):
    """Usage: zenfig [-I <varfile>]... <template_file>

    -I <varfile>, --include <varfile>  Variables file/directory to include
    """

    return docopt(parse_args.__doc__, argv=argv, version=pkg_version)


def _splash():
    """Print the splash"""
    splash_title = "{pkg} [{version}] - {url}".format(
        pkg=pkg_name, version=pkg_version, url=pkg_url)
    log.to_stdout(splash_title, colorf=log.yellow, bold=True)
    log.to_stdout('-' * len(splash_title), colorf=log.yellow, bold=True)
    log.to_stdout(
        "Please, report issues to {}/issues"
        .format(pkg_url), colorf=log.yellow, bold=True
    )

def start(*, options):
    """
    The main thing

    :param options: list of arguments
    """

    # Show splash
    _splash()

    # measure execution time properly
    start_time = time.time()

    # options passed from the command line
    var_files = variables.normalize_search_path(options['--include'])
    log.msg_debug("Variables search path:")
    log.msg_debug("**********************")
    for vf in var_files:
        log.msg_debug(vf)
    log.msg_debug("**********************")
    template_file = options['<template_file>']

    # Obtain variables from variable files
    vars = variables.get_vars(var_files=var_files)

    # Print vars
    log.msg("All variable files have been read.")
    log.msg("**********************************")
    for key, value in vars.items():
        log.msg("{:>16} => '{}'".format(key, value), bold=True)
    log.msg("**********************************")

    # Render that template!
    renderer.render(vars=vars, template_file=template_file)

    dt = time.time() - start_time
    log.msg("Done! ({:.3f} ms)".format(dt*1000))

def _handle_except(e):
    """
    Handle (log) any exception

    :param e: exception to be handled
    """
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    log.msg_err("Unhandled {e} at {file}:{line}: '{msg}'" .format(
        e=exc_type.__name__, file=fname,
        line=exc_tb.tb_lineno, msg=e))
    log.msg_err(traceback.format_exc())
    log.msg_err("An error has occurred!. "
                "For more details, review the logs.")
    return 1

def main(argv=None):
    """
    This is the main thread of execution

    :param argv: list of command line arguments
    """
    # Exit code
    exit_code = 0

    # Log initalization should take place before anything else
    log.init()

    # First, we change main() to take an optional 'argv'
    # argument, which allows us to call it from the interactive
    # Python prompt
    if argv is None:
        argv = sys.argv[1:]

    try:
        # Bootstrap
        options = parse_args(argv)

        # start the thing!
        start(options=options)
    except DocoptExit as dexcept:

        # Deal with wrong arguments
        print(dexcept)
        exit_code = 1
    except Exception as e:

        # ... and if everything else fails
        _handle_except(e)
        exit_code = 1

    return exit_code


# Now the sys.exit() calls are annoying: when main() calls
# sys.exit(), your interactive Python interpreter will exit!.
# The remedy is to let main()'s return value specify the
# exit status.
if __name__ == '__main__':
    sys.exit(main())
