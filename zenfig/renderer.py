# -*- coding: utf-8 -*-

"""
zenfig.renderer
~~~~~~~~

Template renderer

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os
import jinja2

from . import log
from . import api
from . import util

from .util import autolog


class InvalidTemplateDirError(BaseException):
    def __init__(self, directory):
        super().__init__("main.j2 not found in {}".format(directory))

@autolog
def render_dict(vars):
    """
    Render a jinja2-flavored dictionary with itself

    :vars: A dictionary containing expected-to-be jinja2 strings
    :returns: A dictionary whose string values have been rendered with jinja2
    """

    ###########################
    # Load template environment
    ###########################
    tpl_env = jinja2.Environment(loader=jinja2.DictLoader(vars))

    ############################
    # register all API functions
    ############################
    _register_api_entries(tpl_env)

    #############################################
    # Strings found in this dict will be rendered
    # using this same dict as its variables
    # In this fashion, YAML files can have jinja2
    # logic as well, thus, variables in YAML can
    # reference other variables
    #############################################
    for tpl_name, tpl_value in vars.items():
        if isinstance(tpl_value, str):
            vars[tpl_name] = tpl_env.get_template(tpl_name).render(**vars)

    # Give back rendered variables
    return vars

@autolog
def _register_api_entries(tpl_env):
    """Register all API functions"""

    for api_entry, api_func in api.get_map().items():
        tpl_env.globals[api_entry] = api_func

@autolog
def render_file(*, vars, template_file, output_file):
    """
    Render a jinja2 template

    :param vars: a dictionary containing all variables to be injected into the template
    :param template_file: path to the template file
    :param output_file: path to resulting output file
    """

    # Make sure we have the absolute path to the template file
    template_file = os.path.abspath(template_file)

    ##############################################
    # A directory instead of a single file can
    # be specified. In this case, zenfig will
    # look for a file named main.j2 inside that
    # directory
    ##############################################
    if os.path.isdir(template_file):
        template_file = "{}/main.j2".format(template_file)
        log.msg_warn("You have specified a template directory")
        log.msg_warn("I'm gonna look for {}".format(template_file))

        if os.path.isfile(template_file):
            log.msg_warn("{} found!".format(template_file))
        else:
            raise InvalidTemplateDirError(os.path.dirname(template_file))

    ####################################################
    # zenfig will look for templates on this directories
    ####################################################

    # XDG_DATA_HOME/zenfig/templates is inside
    # the template search path
    xdg_template_directory = "{}/templates".format(
        util.get_xdg_data_home()
    )

    # Construct the actual search path
    tpl_searchpath = [
            os.getcwd(), # relative to current working directory
            os.path.dirname(template_file),  # relative to template's directory
            xdg_template_directory,
            '/',  # absolute paths
            ]

    # There are cases in which duplicate entries
    # inside the template search path could actually exist,
    # e.g. cwd and template directory are the same
    tpl_searchpath = sorted(set(tpl_searchpath), key=lambda x: tpl_searchpath.index(x))

    log.msg_debug("Template search path:")
    log.msg_debug("*********************")
    for search_path in tpl_searchpath:
        log.msg_debug(search_path)
    log.msg_debug("*********************")

    ###########################
    # load template environment
    ###########################
    tpl_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(tpl_searchpath),
        trim_blocks=True,
        keep_trailing_newline=True
    )

    # set user's environment variables inside globals
    tpl_env.globals['env'] = os.environ

    ############################
    # register all API functions
    ############################
    _register_api_entries(tpl_env)

    # load the template
    tpl = tpl_env.get_template(template_file)

    ##############################################
    # Render template to destination (output) file
    ##############################################
    log.msg("Rendering template ...")
    rendered_str = tpl.render(**vars)
    if output_file is None:
        # Render to stdout
        print(rendered_str)
    else:
        output_file = os.path.abspath(output_file)
        log.msg("Writing to '{}'".format(output_file), bold=True)
        with open(output_file, 'w') as of:
            of.write(rendered_str)
