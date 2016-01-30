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
from . import api


def render(*, vars, template_file):
    """
    Render a jinja2 template

    :vars: a dictionary containing all variables to be injected into the template
    :template_file: path to the template file
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

    ####################################################
    # zenfig will look for templates on this directories
    ####################################################
    tpl_searchpath = [
            os.getcwd(), # relative to current working directory
            os.path.dirname(template_file),  # relative to template's directory
            '/',  # absolute paths
            ]
    log.msg_debug("Template search path")
    for search_path in tpl_searchpath:
        log.msg_debug(search_path)

    ###########################
    # load template environment
    ###########################
    tpl_loader = jinja2.FileSystemLoader(tpl_searchpath)

    # everything begins with a jinja environment
    tpl_env = jinja2.Environment(loader=tpl_loader, trim_blocks=True)

    # set user's environment variables inside globals
    tpl_env.globals['env'] = os.environ

    ############################
    # register all API functions
    ############################
    for api_entry, api_func in api.get_map().items():
        tpl_env.globals[api_entry] = api_func

    # load the template
    tpl = tpl_env.get_template(template_file)

    # render template to stdout
    log.msg("Rendering template ...")
    print(tpl.render(**vars))
