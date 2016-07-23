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


def _parse_args(argv):
    """Usage: zenfig [-x] [-v]... [-I <varfile>]... (install|preview) <kit>

    -I <varfile>, --include <varfile>  Variables file/directory to include
    -v  Output verbosity
    -x, --defaults-only                Discard any variable locations set by the user
    """

    return docopt(_parse_args.__doc__, argv=argv, version=pkg_version)


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

def _start(*, options):
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

    # Variable locations taken from args
    user_var_files = options['--include']

    ###################################
    # Initialize kit interface:
    # This will deduct what type of kit
    # this is dealing with, it will load
    # the appropiate interface based on
    # kit_name.
    ###################################
    kit_name = options['<kit>']

    # Initialise kit interface
    _kit = kit.get_kit(kit_name)

    ####################
    # Get user variables
    ####################
    user_vars = variables.get_user_vars(
        user_var_files=user_var_files,
        kit=_kit,
        defaults_only=options['--defaults-only'],
    )

    for template_data in _kit.templates.values():

        # Obtain basic information from the kit
        template_file = template_data['path']
        template_include_dirs = template_data['include']

        # Depending on command set, the file would be either
        # displayed on screen or written onto a file
        if not options['preview']:
            output_file = template_data['output_file']
        else:
            log.msg_warn('Previewing file: {}'.format(
                template_data['output_file']
            ))
            log.msg_warn('---')
            output_file = None

        #######################
        # Render that template!
        #######################
        renderer.render_file(
            vars=user_vars,
            template_file=template_file,
            template_include_dirs=template_include_dirs,
            output_file=output_file,
        )

        # Mark the end of previewed file
        if options['preview']:
            log.msg_warn('---')

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
        _start(options=_parse_args(argv))
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
