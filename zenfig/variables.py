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


# Sanity check regex for ZF_VAR_PATH
ZF_VAR_PATH_REGEX = "([^:]+:)*[^:]+$"

def _get_vars_from_env(var_path=None):
    """
    Get variable search paths from environment variable ZF_VAR_PATH (if any)

    :param var_path: optional var_path string
    """

    if var_path is None:
        var_path = os.getenv("ZF_VAR_PATH")
    if var_path is not None and re.match(ZF_VAR_PATH_REGEX, var_path):
        log.msg_debug("ZF_VAR_PATH has been set!")
        return var_path.split(':')
    return None

def normalize_search_path(*, user_var_files, kit_var_dir=None):
    """
    Normalize variable search path

    :param user_var_files: Raw list of variable locations set by the user
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
    for i in range(len(user_var_files)):
        user_var_files[i] = os.path.abspath(user_var_files[i])

    ################################
    # 2 => Variables set in ZF_VAR_PATH
    # Add entries in ZF_VAR_PATH:
    # Should this environment variable
    # be set, then it will be taken into
    # account for variables search path
    ################################
    env_vars = _get_vars_from_env()
    if env_vars is not None:
        user_var_files.extend(env_vars)

    ########################################
    # 3 => Variables set in default vars dir
    # Add XDG_DATA_HOME/zenfig/vars into the
    # search path
    ########################################
    xdg_variables_dir = "{}/vars".format(util.get_xdg_data_home())
    user_var_files.append(xdg_variables_dir)

    ########################################
    # 4 => Default variables set by the package
    # (if specified) in
    # XDG_CACHE_HOME/zenfig/<package>/defaults
    ########################################
    if kit_var_dir is not None:
        user_var_files.append(kit_var_dir)

    # Make sure there are no duplicates in this one
    return sorted(set(user_var_files), key=lambda x: user_var_files.index(x))[::-1]

def get_vars(*, var_files):
    """
    Collect all variables taken from all files in var_files

    :param var_files: list of files/directories to be sourced
    :returns:
        A tuple with two dicts, one containing variables
        and the other one containing locations where they were
        ultimately set (following precedence set by normalize_search_path)
    """

    ######################################
    # All merged variables will go in here
    ######################################
    tpl_vars = {}  # variables themselves
    tpl_files = {}  # locations in which these vars were set will go in here

    #############################################################
    # iterate through all entries and see whether or not they're
    # files or directories
    #############################################################
    for var_file in var_files:

        # Normalize full path to file
        var_file = os.path.abspath(var_file)

        # The entry is in fact a file, thus, to load it directly I must
        # Only files with .yaml and .yml will be taken into account
        if os.path.isfile(var_file) and \
        re.match("/.*\.yaml$", var_file) or re.match("/.*\.yml$", var_file):
            with open(var_file, 'r') as f:
                log.msg_debug("Found variable file: {}".format(var_file))
                log.msg("Reading variables from '{}'".format(var_file))

                # Update variables with those found
                # on this file
                vars = yaml.load(f)
                tpl_vars.update(vars)

                # And update locations in which these
                # variables were found
                for var in vars.keys():
                    tpl_files[var] = var_file

        # The entry is a directory
        elif os.path.isdir(var_file):

            # First of all, list all files inside of this directory
            # and merge their values with tpl_vars
            next_var_files = []
            for next_var_file in os.listdir(var_file):
                next_var_file = os.path.join(var_file, next_var_file)
                if os.path.isfile(next_var_file):
                    next_var_files.append(next_var_file)

            # Get both variables and locations
            vars, files = get_vars(var_files=next_var_files)

            # ... and merge them with the current
            tpl_vars.update(vars)
            tpl_files.update(files)

    # Return the final result
    return tpl_vars, tpl_files

