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

    ####################################################
    # zenfig will look for templates on this directories
    ####################################################
    tpl_searchpath = [
            os.getcwd(), # relative to current working directory
            os.dirname(template_file),  # relative to template's directory
            '/',  # absolute paths
            ]

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
    print(tpl.render(**vars))
