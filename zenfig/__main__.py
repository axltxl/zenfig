# -*- coding: utf-8 -*-

"""
zenfig.main
~~~~~~~~

Main module

:copyright: (c) 2015 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import sys
import os
import time
import traceback
from docopt import docopt
from colour import Color
from docopt import DocoptExit
from zenfig import renderer
from zenfig import log
from zenfig import variables

def parse_args(argv):
    """Usage: zenfig (-I <varfile>)... <template_file>

    -I <varfile>, --include <varfile>  Variables file/directory to include
    """

    return docopt(parse_args.__doc__, argv=argv)

def start(*, options):
    """the main thing"""

    # measure execution time properly
    start_time = time.time()

    # options passed from the command line
    var_files = options['--include']
    template_file = options['<template_file>']

    # Obtain variables from variable files
    log.msg_debug("tpl_var_files = {}".format(var_files))
    vars = variables.get_vars(var_files=var_files)

    log.msg("All variable files have been read.")
    log.msg("----------------------------------")
    for key, value in vars.items():
        log.msg("{:10} => '{}'".format(key, value), bold=True)
    log.msg("----------------------------------")

    log.msg("Rendering template ...")
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
