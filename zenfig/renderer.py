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
from .depgraph.depgraph import DepGraph
from .depgraph.node import Node


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


class VarNode(Node):
    """Variable node implementation"""

    def calc_deps(self, value=None):
        """
        Calculate dependencies for this node

        :param value: value to be evaluated for dependencies
        """

        # All collected dependencies' keys will go in here
        deps = []

        # Since this method is recursive, it is capable of evaluating
        # as deep as the value goes, meaning that it can check dictionaries
        # and lists for any references of dependencies. At first, this
        # value is this node's value itself, if required, this method
        # is recursively called until all dependencies have been collected.
        if value is None:
            value = self.value

        # Only strings are actually checked for dependencies
        if isinstance(value, str):
            # References to @variables within {{ jinja blocks }} are
            # considered by this node as references to dependencies.
            # They are isolated and collected.
            for jinja_blk in REGEX_JINJA2.findall(value):
                for var_name in REGEX_VAR.findall(value):
                    dep_name = REGEX_VAR_STRIP.sub('', var_name)
                    deps.append(dep_name)

        # dict found?, its values are checked as well for any dependencies
        elif isinstance(value, dict):
            for dval in value.values():
                deps.extend(self.calc_deps(dval))

        # list found?, its values are checked one by one to see whether
        # there are any references to dependencies.
        elif isinstance(value, list):
            for lval in value:
                deps.extend(self.calc_deps(lval))

        # All scavenged dependencies are returned
        return deps

    @staticmethod
    def _render(value, deps):
        """
        Render a string through jinja2

        :param value: value to be rendered
        :param deps: a list of variables to be applied upon rendering
        :returns: A jinja2-rendered string
        """
        tpl = {'@': value}

        tpl_vars = {}
        for dep_name, dep_node in deps.items():
            tpl_vars[dep_name] = dep_node.value
        # so we can render this value
        # Load template environment
        tpl_env = jinja2.Environment(loader=jinja2.DictLoader(tpl))

        # Register all globals and filters
        _register_api(tpl_env)

        # Render and deliver, finally!
        return tpl_env.get_template('@').render(tpl_vars)

    def on_evaluate(self, value=None):
        """Evaluate this node"""

        # Bootstrap this thing with its first value
        if value is None:
            return self.on_evaluate(self.value)

        # no point if there are no dependencies whatsoever.
        if not len(self.deps):
            return self.value

        # Each string found will be treated with already evaluated
        # dependencies values
        if isinstance(value, str):

            # Each dependency replaces its references within this node's value
            for dep_name, dep_node in self.deps.items():

                # Actual value substitution
                # on node's.value (which is the resulting
                # value from resolution)
                if isinstance(dep_node.value, str):
                    var_fmt = '"{}"'
                else:
                    var_fmt = '{}'

                var_pattern = REGEX_FMT_VAR.format(dep_name)
                var_repl = var_fmt.format(dep_node.value)
                value = re.sub(var_pattern, var_repl, value)

            # Once all dependencies have been put in place
            # time to render
            return self._render(value, self.deps)

        # Check for each element in this dict and evaluate it accordingly
        elif isinstance(value, dict):
            for dkey, dval in value.items():
                value[dkey] = self.on_evaluate(dval)

        # Check for each element in the list and evaluate it accordingly
        elif isinstance(value, list):
            for i, lval in enumerate(value):
                value[i] = self.on_evaluate(lval)

        # At this point, whichever value it was being evaluated, it
        # got evaluated, so ...
        return value


@autolog
def render_dict(**kwargs):
    """
    Render a jinja2-flavored dictionary with itself

    :kwargs: A dictionary containing expected-to-be jinja2 strings
    :returns: A dictionary whose string values have been rendered with jinja2
    """

    #############################################
    # Strings found in this dict will be rendered
    # using this same dict as its variables
    # In this fashion, YAML files can have jinja2
    # logic as well, thus, variables in YAML can
    # reference other variables
    #############################################

    return DepGraph(node_class=VarNode, **kwargs).evaluate()


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
        extensions = [
            'jinja2.ext.do',
            'jinja2.ext.loopcontrols',
            'jinja2.ext.with_'
            ]
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
