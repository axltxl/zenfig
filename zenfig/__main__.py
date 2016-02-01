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
from zenfig import package

def parse_args(argv):
    """Usage: zenfig [-v]... [-I <varfile>]... [-o <file>] (<template_file> | -p <package>)

    -p, --package <package>  Render package (needs better explanation)
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

    #
    #TODO: comment this!
    template_file = options['<template_file>']
    package_name = options['--package']
    package_var_files = None
    user_var_files = options['--include']

    #
    #TODO: implement this!
    if template_file is None:
        # update packages cache (git repo)
        package.update_cache()

        #
        package_var_files = package.get_var_dir(package_name)

    ##########################
    # Get variable search path
    ##########################
    user_var_files = variables.normalize_search_path(
        user_var_files=user_var_files,
        package_var_files=package_var_files
    )
    log.msg_debug("Variables search path:")
    log.msg_debug("**********************")
    for vf in user_var_files:
        log.msg_debug(vf)
    log.msg_debug("**********************")

    #
    #TODO: implement this!
    if template_file is None:
        # get template main dir from package
        template_file = package.get_template_dir(package_name)

    # Obtain variables from variable files
    vars, files = variables.get_vars(
        user_var_files=user_var_files,
        package_var_files=package_var_files
    )
    vars = renderer.render_dict(vars)

    # Print vars
    log.msg("All variable files have been read.")
    log.msg("**********************************")
    for key, value in vars.items():
        log.msg("{:16} => '{}' [{}]".format(key, value, files[key]), bold=True)
    log.msg("**********************************")

    #######################
    # Render that template!
    #######################
    output_file = options['--output-file']
    renderer.render_file(
        vars=vars, template_file=template_file,
        output_file=output_file
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


    # First, we change main() to take an optional 'argv'
    # argument, which allows us to call it from the interactive
    # Python prompt
    if argv is None:
        argv = sys.argv[1:]

    try:
        # Bootstrap
        options = parse_args(argv)

        # start the thing!
        start(options=parse_args(argv))
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
