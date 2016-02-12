# -*- coding: utf-8 -*-

"""
zenfig.renderer
~~~~~~~~

Template renderer

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os
import re
import jinja2

from . import log
from . import api
from . import util

from .util import autolog


class InvalidTemplateDirError(BaseException):
    """Basic exception for invalid kits"""

    def __init__(self, directory):
        super().__init__("main.j2 not found in {}".format(directory))

# Regular expression strings used
# for variable isolation during resolution
# by _var_resolve
REGEX_PATT_JINJA2 = '{{.+}}'
REGEX_JINJA2 = re.compile(REGEX_PATT_JINJA2)

# Regular expressions for _var_strip
REGEX_PATT_VAR = '@[0-9A-Za-z-_]+'
REGEX_FMT_VAR = '@{}'
REGEX_FMT_VAR_STRIP = '[@]'
REGEX_VAR = re.compile(REGEX_PATT_VAR)
REGEX_VAR_STRIP = re.compile(REGEX_FMT_VAR_STRIP)


@autolog
def _var_strip(
    vars,
    name,
    tpl_val_jinja_blk,
    tpl_value,
    *,
    regex_var,
    regex_var_strip,
    regex_fmt_var
):
    """
    Variable substitution

    Tokenize variables from a jinja2 block and substitute them
    with their resolved variables.

    :param vars: A list of all variables to be used
    :param tpl_var_jinja_blk: A jinja2 block string
    :param tpl_value: Value of the variable 'name'
    :param name: Name of the whose value is going to be resolved
    :param regex_var: Regular expression for variable tokenization
    :param regex_var_strip: Regular expression for variable stripping
    :param regex_fmt_var: String format for variable reinsertion into tpl_val_jinja_blk
    :returns: A jinja2 string with all inner variables resolved
    """

    for tpl_val_var_name in regex_var.findall(tpl_val_jinja_blk):

        # strip surrounding chars
        tpl_val_var_name = regex_var_strip.sub('', tpl_val_var_name)

        # resolve this variable
        vars[tpl_val_var_name] = _var_resolve(tpl_val_var_name, vars=vars)

        # Once tpl_val_var_name, has been resolved
        # then proceed to actual value substitution
        # on tpl_value (which is the resulting value from resolution)
        if isinstance(vars[name], str):
            var_fmt = '"{}"'
        else:
            var_fmt = ''

        # Variable reinsertion into tpl_value
        # Each resolved variable that was inside each jinja2 block
        # is replaced with its resolved value
        tpl_value = re.sub(
            regex_fmt_var.format(tpl_val_var_name),
            var_fmt.format(vars[tpl_val_var_name]),
            tpl_value
        )

    # give the thing back!
    return tpl_value


@autolog
def _var_resolve(name, *, vars):
    """
    Resolve a variable

    Deduct the value of a variable in vars

    :param name: the needle
    :param vars: the haze
    """

    # Only strings are resolved
    if not isinstance(vars[name], str):
        return vars[name]

    # We begin by getting current string value
    # held by this var
    tpl_value = vars[name]

    ##########################################################################
    # Variable recursive resolution:
    # ------------------------------
    # Variables must be inside jinja2 blocks in order for them to be resolved.
    # If other variables are found inside jinja2 blocks, them these are
    # firstly resolved recursively
    ##########################################################################
    for tpl_val_jinja_blk in REGEX_JINJA2.findall(tpl_value):
        # Resolve each variable inside each jinja2 block
        tpl_value = _var_strip(
            vars, name, tpl_val_jinja_blk, tpl_value,
            regex_var=REGEX_VAR, regex_var_strip=REGEX_VAR_STRIP,
            regex_fmt_var=REGEX_FMT_VAR
        )

    #############################################################
    # At this point, all dependent variables have been resolved
    # However, they are still jinja2 blocks
    # Meaning, we have to deliver them to jinja2 in order to have
    # a full resolved value
    #############################################################

    # Reasign tpl_value to current var to be rendered
    vars[name] = tpl_value

    # so we can render this value
    if REGEX_JINJA2.match(vars[name]):
        # Load template environment
        tpl_env = jinja2.Environment(loader=jinja2.DictLoader(vars))

        # Register all globals and filters
        _register_api(tpl_env)

        # Render and deliver, finally!
        return tpl_env.get_template(name).render(vars)

    # At this point, this string value must be constant,
    # namely, it has no jinja2 blocks whatsoever
    return tpl_value


@autolog
def render_dict(vars):
    """
    Render a jinja2-flavored dictionary with itself

    :vars: A dictionary containing expected-to-be jinja2 strings
    :returns: A dictionary whose string values have been rendered with jinja2
    """

    #############################################
    # Strings found in this dict will be rendered
    # using this same dict as its variables
    # In this fashion, YAML files can have jinja2
    # logic as well, thus, variables in YAML can
    # reference other variables
    #############################################
    tpl_vars_keys = [
        k for k, v in vars.items()
        if isinstance(v, str) and REGEX_JINJA2.match(v)
    ]
    for tpl_name in tpl_vars_keys:
        vars[tpl_name] = _var_resolve(tpl_name, vars=vars)

    # Give back rendered variables
    return vars


def _register_api(tpl_env):
    """Register custom globals and filters"""

    _register_api_globals(tpl_env)
    _register_api_filters(tpl_env)


@autolog
def _register_api_globals(tpl_env):
    """Register all globals"""

    for api_global_name, api_global_func in api.get_globals().items():
        tpl_env.globals[api_global_name] = api_global_func


@autolog
def _register_api_filters(tpl_env):
    """Register all filters"""

    for api_filter_name, api_filter_func in api.get_filters().items():
        tpl_env.filters[api_filter_name] = api_filter_func


@autolog
def render_file(*, vars, template_file, output_file, template_include_dirs):
    """
    Render a jinja2 template

    :param vars:
        a dictionary containing all variables to be injected into the template
    :param template_file: path to the template file
    :param output_file: path to resulting output file
    :param template_include_dirs: template include directories
    """

    ####################################################
    # zenfig will look for templates on this directories
    ####################################################

    # There are cases in which duplicate entries
    # inside the template search path could actually exist,
    # e.g. cwd and template directory are the same
    template_include_dirs = sorted(
        set(template_include_dirs),
        key=lambda x: template_include_dirs.index(x)
    )

    # XDG_DATA_HOME/templates is also added to the template search path:
    # This is mostly because there are kits that offer the user to include
    # his own custom templates as a means of customization and expansion.
    template_include_dirs.append(
        os.path.join(util.get_xdg_data_home(), 'templates')
    )

    log.msg_debug("Template search path:")
    log.msg_debug("*********************")
    for search_path in template_include_dirs:
        log.msg_debug(search_path)
    log.msg_debug("*********************")

    ###########################
    # load template environment
    ###########################
    tpl_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_include_dirs),
        trim_blocks=True,
        keep_trailing_newline=True,
        line_comment_prefix="#",
        line_statement_prefix="%",
    )

    ############################
    # register all API functions
    ############################
    _register_api(tpl_env)

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
        with open(output_file, 'w') as ofile:
            ofile.write(rendered_str)
