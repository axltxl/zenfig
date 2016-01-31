# -*- coding: utf-8 -*-

"""
zenfig.variables
~~~~~~~~

Variables processor

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import yaml
import re
import os

from . import log
from . import util

def normalize_search_path(var_files):
    """
    Normalize variable search path

    :param var_files: Raw list of variable locations
    :returns: A normalized list of variable locations/files, ordered by precedence
    """

    ########################################
    # Variable locations are set by order of
    # precedence as follows
    ########################################

    #####################################
    # 1 => Variables set by the user
    # Make sure we have absolute paths to
    # all variable files and/or directories
    #####################################
    for i in range(len(var_files)):
        var_files[i] = os.path.abspath(var_files[i])

    ################################
    # 2 => Variables set in ZF_VAR_PATH
    # Add entries in ZF_VAR_PATH:
    # Should this environment variable
    # be set, then it will be taken into
    # account for variables search path
    ################################
    env_var_path = os.getenv("ZF_VAR_PATH")
    if env_var_path is not None:
        log.msg_warn("ZF_VAR_PATH has been set!")
        env_var_files = env_var_path.split(":")
        for env_var_file in env_var_files:
            var_files.append(env_var_file)

    ########################################
    # 3 => Variables set in default vars dir
    # Add XDG_DATA_HOME/zenfig/vars into the
    # search path
    ########################################
    xdg_variables_dir = "{}/vars".format(util.get_xdg_data_home())
    var_files.append(xdg_variables_dir)

    # Make sure there are no duplicates in this one
    return sorted(set(var_files), key=lambda x: var_files.index(x))[::-1]

def get_vars(*, var_files):
    """
    Collect all variables taken from all files in var_files

    :param var_files: list of files/directories to be sourced
    :returns: A dictionary containing all variables collected from all set locations
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

