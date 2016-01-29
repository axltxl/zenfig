# -*- coding: utf-8 -*-

"""
zenfig.variables
~~~~~~~~

Variables processor

:copyright: (c) 2015 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import yaml
import os


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

        # The entry is in fact a file
        # thus, to load it directly I must
        if os.path.isfile(var_file):
            with open(var_file, 'r') as f:
                tpl_vars.update(yaml.load(f))

        # The entry is a directory
        elif os.path.isdir(var_file):

            # First of all, list all files inside of this directory
            # and merge their values with tpl_vars
            for next_var_file in os.listdir(var_file):
                next_var_file = os.path.join(var_file, next_var_file)
                if os.path.isfile(next_var_file):
                    with open(next_var_file, 'r') as f:
                        tpl_vars.update(yaml.load(f))

    # Return the final result
    return tpl_vars

