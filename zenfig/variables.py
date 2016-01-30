# -*- coding: utf-8 -*-

"""
zenfig.variables
~~~~~~~~

Variables processor

:copyright: (c) 2015 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import yaml
import re
import os

from . import log

def get_vars(*, var_files):
    """Collect all variables taken from all files in var_files

    Kwargs:
        var_files(list): list of files/directories to be sourced
    """

    # All merged variables will go in here
    tpl_vars = {}

    #############################################################
    # iterate through all entries and see whether or not they're
    # files or directories
    #############################################################
    for var_file in var_files:

        # Normalize full path to file
        var_file = os.path.abspath(var_file)
        log.msg("Attempting to read from '{}'".format(var_file))

        # The entry is in fact a file, thus, to load it directly I must
        # Only files with .yaml and .yml will be taken into account
        if os.path.isfile(var_file) and \
        re.match("/.*\.yaml$", var_file) or re.match("/.*\.yml$", var_file):
            with open(var_file, 'r') as f:
                log.msg_debug("Found variable file: {}".format(var_file))
                tpl_vars.update(yaml.load(f))

        # The entry is a directory
        elif os.path.isdir(var_file):

            # First of all, list all files inside of this directory
            # and merge their values with tpl_vars
            next_var_files = []
            for next_var_file in os.listdir(var_file):
                next_var_file = os.path.join(var_file, next_var_file)
                if os.path.isfile(next_var_file):
                    next_var_files.append(next_var_file)
            tpl_vars.update(get_vars(var_files=next_var_files))

    # Return the final result
    return tpl_vars

