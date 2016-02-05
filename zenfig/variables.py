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
from . import renderer
from .util import autolog


# Sanity check regex for ZF_VAR_PATH
ZF_VAR_PATH_REGEX = "([^:]+:)*[^:]+$"

@autolog
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

@autolog
def _resolve_search_path(*, user_var_files, kit_var_dir=None):
    """
    Resolve variable search path

    :param user_var_files: Raw list of variable locations set by the user
    :returns:
        A list of variable locations/files, ordered by precedence
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

@autolog
def _get_default_vars():
    """
    Get default variables

    Default variables are mutable global variables
    covering a great range of basics, from common terminal settings
    to color schemes. Since they are mutable, it means that they
    can be superseeded by other definitions found along the variable
    resolution with set search paths.

    :return: A dictionary with a bunch of scavenged variables
    """

    # This holds the entire thing
    default_vars = {}

    # Browser settings
    browser = os.getenv("BROWSER")
    if browser is None:
        browser = 'firefox'
    default_vars["browser"] = browser

    #################################
    # base16 colors (default palette)
    #################################
    base16_colors = [
        "181818",
        "282828",
        "383838",
        "585858",
        "b8b8b8",
        "d8d8d8",
        "e8e8e8",
        "f8f8f8",
        "ab4642",
        "dc9656",
        "f7ca88",
        "a1b56c",
        "86c1b9",
        "7cafc2",
        "ba8baf",
        "a16946",
    ]
    # Insert on defaults
    for index, color in enumerate(base16_colors):
        index = "{:02x}".format(index).upper()
        default_vars["color_base{}".format(index)] = color

    ###############
    # Font settings
    ###############
    font_settings = {
        "font": "Sans",
        "font_size": 10,
        "font_antialiasing": True,
        "font_hinting": True,
    }

    # Insert on defaults
    default_vars.update(font_settings)

    ##########################
    # Terminal common settings
    ##########################
    term_settings = {
        "term": os.getenv("TERM"),
        "term_font": "Mono",
        "term_scroll_on_output": True,
        "term_font_size": 10,

        ####################################################
        # Notice that terminal color values
        # depend ultimately on resolved base16 color palette
        # from variables, hence the reason why they are actual
        # string templates.
        ####################################################

        # 16-color space
        "term_color00": "{{ @color_base00 }}",
        "term_color01": "{{ @color_base08 }}",
        "term_color02": "{{ @color_base0B }}",
        "term_color03": "{{ @color_base0A }}",
        "term_color04": "{{ @color_base0D }}",
        "term_color05": "{{ @color_base0E }}",
        "term_color06": "{{ @color_base0C }}",
        "term_color07": "{{ @color_base05 }}",
        "term_color08": "{{ @color_base03 }}",
        "term_color09": "{{ @color_base08 }}",
        "term_color10": "{{ @color_base0B }}",
        "term_color11": "{{ @color_base0A }}",
        "term_color12": "{{ @color_base0D }}",
        "term_color13": "{{ @color_base0E }}",
        "term_color14": "{{ @color_base0E }}",
        "term_color15": "{{ @color_base07 }}",

        # 256-color space
        "term_color16": "{{ @color_base09 }}",
        "term_color17": "{{ @color_base0F }}",
        "term_color18": "{{ @color_base01 }}",
        "term_color19": "{{ @color_base02 }}",
        "term_color20": "{{ @color_base04 }}",
        "term_color21": "{{ @color_base06 }}",
    }
    # Insert on defaults
    default_vars.update(term_settings)

    # Give those variables already!
    return default_vars

@autolog
def _get_builtin_vars():
    """
    Get built-in variables

    Built-in variables are immutable global variables
    set at the very end of variable resolution.

    :return: A dictionary with a bunch of scavenged variables
    """

    # The very basics
    path = os.getenv("PATH").split(":")
    home = os.getenv("HOME")

    # Give those variables already!
    return {
        "path": path,
        "home": home
    }

@autolog
def get_user_vars(*, user_var_files, kit_var_dir):
    """
    Resolve variables from user environment

    This compiles all set variables to be applied
    on the template. These variables come from defaults,
    read-only built-ins, kits (if specified),
    files found in default search paths and
    ultimately search paths set by the user.

    :param user_var_files: Variable search paths set by the user
    :param kit_var_dir: Kit search path
    """

    #######################################################
    # User variables get initialised with default variables
    #######################################################
    user_vars = _get_default_vars()
    user_var_locations = {}
    # set locations
    for user_var in user_vars.keys():
        user_var_locations[user_var] = None

    ##########################
    # Get variable search path
    ##########################
    user_var_files = _resolve_search_path(
        user_var_files=user_var_files,
        kit_var_dir=kit_var_dir
    )
    log.msg_debug("Variables search path:")
    log.msg_debug("**********************")
    for user_var_file in user_var_files:
        log.msg_debug(user_var_file)
    log.msg_debug("**********************")

    ########################################
    # Set builtin variables
    # They are set at this point so they are
    # sort-of read-only
    ########################################
    builtin_vars = _get_builtin_vars()
    builtin_var_locations = {}
    for builtin_var in builtin_vars.keys():
        builtin_var_locations[builtin_var] = None
    user_vars.update(builtin_vars)
    user_var_locations.update(builtin_var_locations)

    ######################################################
    # Obtain variables from variable files set by the user
    ######################################################
    vars, locations = _get_vars(var_files=user_var_files)
    user_vars.update(vars)

    # Variables whose values are strings may
    # have jinja2 logic within them as well
    # so we render those values through jinja
    # so, we merge defaults and builtins with
    # user-set values to get the final picture
    user_vars.update(renderer.render_dict(user_vars))

    # and we consolidate their locations (should they come from actual files)
    user_var_locations.update(locations)

    # Print vars
    list_vars(vars=user_vars, locations=user_var_locations)

    # Give variables already!
    return user_vars

@autolog
def list_vars(*, vars, locations):
    """Print all vars given"""

    log.msg("{} variable(s) captured".format(len(vars)))
    log.msg("**********************************")
    for key, value in sorted(vars.items()):
        location = locations[key]
        if location is None:
            location = "built-in"
        if isinstance(value, list):
            log.msg("{:24} [list] [{}]".format(key, location))
            for subvalue in value:
                log.msg("    => {}".format(subvalue))
        elif isinstance(value, dict):
            log.msg("{:24} [list] [{}]".format(key, location))
            for k, v in value:
                log.msg("  {:24}  => {}".format(k, v))
        else:
            log.msg("{:24} = '{}' [{}]".format(key, value, location))
    log.msg("**********************************")

@autolog
def _get_vars(*, var_files):
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

        ###############################################################
        # The entry is in fact a file, thus, to load it directly I must
        # Only files with .yaml and .yml will be taken into account
        ###############################################################
        # The entry is in fact a file, thus, to load it directly I must
        if os.path.isfile(var_file) and \
        re.match("/.*\.yaml$", var_file) or re.match("/.*\.yml$", var_file):
            with open(var_file, 'r') as f:
                # Update variables with those found
                # on this file
                try:
                    vars = yaml.load(f)
                    tpl_vars.update(vars)
                    # And update locations in which these
                    # variables were found
                    for var in vars.keys():
                        tpl_files[var] = var_file

                    # Log the count
                    log.msg_debug("Found {} variable(s) in {}".format(
                        len(vars), var_file)
                    )
                except yaml.YAMLError as exc:
                    log.msg_err("Error loading variable file: {}".format(
                        var_file)
                    )
                    log.msg_err("{}: file discarded".format(var_file))


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
            vars, files = _get_vars(var_files=next_var_files)

            # ... and merge them with the current
            tpl_vars.update(vars)
            tpl_files.update(files)

    # Return the final result
    return tpl_vars, tpl_files

