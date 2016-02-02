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
from zenfig import kit

def parse_args(argv):
    """Usage: zenfig [-v]... [-I <varfile>]... [-o <file>] (<template_file> | -k <kit>)

    -k, --kit <kit>  Render kit (needs better explanation)
    -I <varfile>, --include <varfile>  Variables file/directory to include
    -v  Output verbosity
    -o FILE, --output-file FILE  Output file
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

    # Log initalization should take place
    # before anything else
    quiet_stdout = not bool(options['-v'])
    log.init(quiet_stdout=quiet_stdout)

    # Show splash
    _splash()

    # measure execution time properly
    start_time = time.time()

    # Template file taken from args
    template_file = options['<template_file>']

    # Variable locations taken from args
    user_var_files = options['--include']


    ###################################
    # Initialize kit interface:
    # This will deduct what type of kit
    # this is dealing with, it will load
    # the appropiate interface based on
    # kit_name.
    ###################################
    kit_name = options['--kit']
    kit_var_dir = None

    if template_file is None:

        # Initialise kit interface
        kit.init(kit_name)

        # Get variables location for this kit
        kit_var_dir = kit.get_var_dir(kit_name)

        # get template main dir from kit
        template_file = kit.get_template_dir(kit_name)

        # mark the thing
        log.msg_warn("Found kit: {}".format(kit_name))

    ####################
    # Get user variables
    ####################
    user_vars = variables.get_user_vars(
        user_var_files=user_var_files,
        kit_var_dir=kit_var_dir
    )

    #######################
    # Render that template!
    #######################
    output_file = options['--output-file']
    renderer.render_file(
        vars=user_vars,
        template_file=template_file,
        output_file=output_file,
    )

    # Measure execution time
    log.msg("Done! ({:.3f} ms)".format((time.time() - start_time)*1000))

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
    log.msg_debug(traceback.format_exc())
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

    # First, we change main() to take an optional 'argv'
    # argument, which allows us to call it from the interactive
    # Python prompt
    if argv is None:
        argv = sys.argv[1:]

    try:
        # start the thing!
        start(options=parse_args(argv))
    except DocoptExit as dexcept:
        # Deal with wrong arguments
        print(dexcept)
        exit_code = 1
    except BaseException as e:
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
