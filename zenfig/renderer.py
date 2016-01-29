# -*- coding: utf-8 -*-

"""
zenfig.renderer
~~~~~~~~

Template renderer

:copyright: (c) 2015 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os
import jinja2
from . import api


def render(*, vars, template_file):
    """Render a jinja2 template

    :*: TODO
    :vars: TODO
    :template_file: TODO
    :returns: TODO

    """

    # load template environment
    tpl_loader = jinja2.FileSystemLoader(os.getcwd())

    # everything begins with a jinja environment
    tpl_env = jinja2.Environment(loader=tpl_loader, trim_blocks=True)

    # set user's environment variables inside globals
    tpl_env.globals['env'] = os.environ

    # register all API functions
    api.register(tpl_env)

    # load the template
    tpl = tpl_env.get_template(template_file)

    # render template to stdout
    print(tpl.render(**vars))
