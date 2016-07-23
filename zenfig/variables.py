# -*- coding: utf-8 -*-

"""
zenfig.variables
~~~~~~~~

Variables processor

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os
import re
import platform
import yaml
import psutil
import cpuinfo

from . import __name__ as pkg_name
from . import __version__ as pkg_version
from . import log
from . import util
from . import renderer
from .kit import get_kit
from .kits import Kit
from .util import autolog


# Sanity check regex for ZF_VAR_PATH
ZF_VAR_PATH_REGEX = "([^:]+:)*[^:]+$"


@autolog
def _get_search_path_from_env(var_path=None):
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
def _resolve_search_path(*, user_var_files, kit_var_dir=None, defaults_only=False):
    """
    Resolve variable search path

    :param user_var_files: Raw list of variable locations set by the user
    :param defaults_only: If True, variable locations set by the user won't be included.
    :returns:
        A list of variable locations/files, ordered by precedence
    """

    ########################################
    # Variable locations are set by order of
    # precedence as follows
    ########################################

    if not defaults_only:
        #####################################
        # 1 => Variables set by the user
        # Make sure we have absolute paths to
        # all variable files and/or directories
        #####################################
        for i, var_file in enumerate(user_var_files):
            user_var_files[i] = os.path.abspath(user_var_files[i])

        ################################
        # 2 => Variables set in ZF_VAR_PATH
        # Add entries in ZF_VAR_PATH:
        # Should this environment variable
        # be set, then it will be taken into
        # account for variables search path
        ################################
        env_vars = _get_search_path_from_env()
        if env_vars is not None:
            user_var_files.extend(env_vars)

        ########################################
        # 3 => Variables set in default vars dir
        # Add user data home into the search path
        ########################################
        user_vars_dir = "{}/vars".format(util.get_data_home())
        user_var_files.append(user_vars_dir)

    ########################################
    # 4 => Default variables set by the kit
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
        "font_icon": "FontAwesome",
        "font_size": 10,
        "font_antialiasing": True,
        "font_hinting": True,
        "font_hintstyle": "hintslight",
        "font_antialias": True
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

        # general colors
        "term_color_background": "{{ @color_base00 }}",
        "term_color_foreground": "{{ @color_base07 }}",
        "term_color_cursor": "{{ @color_base0A }}",

        # 16-color space
        "term_color00": "{{ @color_base01 }}",
        "term_color01": "{{ @color_base09 }}",
        "term_color02": "{{ @color_base0B }}",
        "term_color03": "{{ @color_base0A }}",
        "term_color04": "{{ @color_base0C }}",
        "term_color05": "{{ @color_base0E }}",
        "term_color06": "{{ @color_base0C }}",
        "term_color07": "{{ @color_base07 }}",
        "term_color08": "{{ @color_base00 }}",
        "term_color09": "{{ @color_base08 }}",
        "term_color10": "{{ @color_base0B }}",
        "term_color11": "{{ @color_base0A }}",
        "term_color12": "{{ @color_base0D }}",
        "term_color13": "{{ @color_base0E }}",
        "term_color14": "{{ @color_base0C }}",
        "term_color15": "{{ @color_base06 }}",

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


def _create_fact(facts, key, value, *, prefix=None):
    if prefix is None:
        prefix = pkg_name
    facts["{}_{}".format(prefix, key)] = value


@autolog
def _get_facts(*, kit=None):
    """
    Get facts

    Facts are immutable global variables
    set at the very end of variable resolution.

    :param kit: A kit from which facts are going to be extracted
    :return: A dictionary with a bunch of scavenged variables
    """

    # these are the facts
    facts = {}

    # General facts that are available for every platform
    _create_fact(facts, 'version', pkg_version)
    _create_fact(facts, 'install_prefix', os.getenv('HOME'))

    # General system-related facts
    _create_fact(facts, 'sys_uid', os.getuid())
    _create_fact(facts, 'sys_gid', os.getgid())

    # A collection of current environment variables is held in here
    _create_fact(facts, 'env', dict(os.environ))

    # Facts for *nix operating systems
    _create_fact(facts, 'sys_path', os.getenv("PATH").split(":"))
    if os.name == 'posix':
        _create_fact(facts, 'sys_user', os.getenv('USER'))
        _create_fact(facts, 'sys_user_home', os.getenv('HOME'))

    ####################################################
    # System-related facts:
    # ---------------------
    # These facts collect characteristics of the current
    # platform zenfig is running on
    ####################################################

    # Operating System facts
    _system = platform.system()
    _create_fact(facts, 'system', _system)
    _create_fact(facts, 'sys_node', platform.node())

    # These are exclusive to linux-based systems
    if _system == 'Linux':
        linux_distro = platform.linux_distribution()
        _create_fact(facts, 'linux_dist_name', linux_distro[0])
        _create_fact(facts, 'linux_dist_version', linux_distro[1])
        _create_fact(facts, 'linux_dist_id', linux_distro[2])

        # kernel version
        _create_fact(facts, 'linux_release', platform.release())

    # OSX-specific facts
    if _system == 'Darwin':
        _create_fact(facts, 'osx_ver', platform.mac_ver())

    # Hardware-related facts
    _create_fact(facts, 'sys_machine', platform.machine())

    # Low level CPU information (thanks to cpuinfo)
    _cpu_info = cpuinfo.get_cpu_info()
    _create_fact(facts, 'cpu_vendor_id', _cpu_info['vendor_id'])
    _create_fact(facts, 'cpu_brand', _cpu_info['brand'])
    _create_fact(facts, 'cpu_cores', _cpu_info['count'])
    _create_fact(facts, 'cpu_hz', _cpu_info['hz_advertised_raw'][0])
    _create_fact(facts, 'cpu_arch', _cpu_info['arch'])
    _create_fact(facts, 'cpu_bits', _cpu_info['bits'])

    # RAM information
    _create_fact(facts, 'mem_total', psutil.virtual_memory()[0])

    ####################
    # Python information
    ####################
    _py_ver = platform.python_version_tuple()
    _create_fact(facts, 'python_implementation', platform.python_revision())
    _create_fact(facts, 'python_version', platform.python_version())
    _create_fact(facts, 'python_version_major', _py_ver[0])
    _create_fact(facts, 'python_version_minor', _py_ver[1])
    _create_fact(facts, 'python_version_patch', _py_ver[2])

    # Kit index variables are taken as well as facts
    # so they can be referenced by other variables, also
    # this means that index variables from a kit can reference
    # other variables as well, because all these variables get
    # rendered as part of variable resolution.
    if kit is not None:
        for key, value in kit.index_data.items():
            _create_fact(facts, key, value, prefix="{}_{}".format(pkg_name, "kit"))

    # Give those variables already!
    return facts


@autolog
def get_user_vars(*, user_var_files=None, kit=None, defaults_only=False):
    """
    Resolve variables from user environment

    This compiles all set variables to be applied
    on the template. These variables come from defaults,
    read-only built-ins, kits (if specified),
    files found in default search paths and
    ultimately search paths set by the user.

    :param user_var_files: Variable search paths set by the user
    :param kit: Kit to be sourced
    :param defaults_only: If True, variable locations set by the user won't be included.
    """

    # user var locations can be None
    if user_var_files is None:
        user_var_files = []

    # Kit variables directory
    kit_var_dir = None

    # Get kit (if any)
    if kit is not None:
        if isinstance(kit, str):
            kit = get_kit(kit)
        elif not isinstance(kit, Kit):
            raise TypeError("kit must be either a str or a Kit")

        # Where is that kit's variable directory?
        kit_var_dir = kit.var_dir

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
        kit_var_dir=kit_var_dir,
        defaults_only=defaults_only
    )
    log.msg_debug("Variables search path:")
    log.msg_debug("**********************")
    for user_var_file in user_var_files:
        log.msg_debug(user_var_file)
    log.msg_debug("**********************")

    ########################################
    # Set facts
    ########################################
    facts = _get_facts(kit=kit)
    fact_locations = {}
    for fact in facts.keys():
        fact_locations[fact] = 'fact'
    user_vars.update(facts)
    user_var_locations.update(fact_locations)

    ######################################################
    # Obtain variables from variable files set by the user
    ######################################################
    _vars, locations = _get_vars(var_files=user_var_files)
    user_vars.update(_vars)

    # Variables whose values are strings may
    # have jinja2 logic within them as well
    # so we render those values through jinja
    # so, we merge defaults and facts with
    # user-set values to get the final picture
    user_vars.update(renderer.render_dict(**user_vars))

    # and we consolidate their locations (should they come from actual files)
    user_var_locations.update(locations)

    # Print vars
    _list_vars(vars=user_vars, locations=user_var_locations)

    # Give variables already!
    return user_vars


@autolog
def _list_vars(*, vars, locations):
    """Print all vars given"""

    log.msg("{} variable(s) captured".format(len(vars)))
    log.msg("**********************************")
    for key, value in sorted(vars.items()):
        location = locations[key]
        if location is None:
            location = "default"
        if isinstance(value, list):
            log.msg("{:24} [list] [{}]".format(key, location))
            for subvalue in value:
                log.msg("    => {}".format(subvalue))
        elif isinstance(value, dict):
            log.msg("{:24} [dict] [{}]".format(key, location))
            for k, v in value.items():
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
