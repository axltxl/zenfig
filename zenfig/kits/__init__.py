# -*- coding: utf-8 -*-

"""
zenfig.kits
~~~~~~~~

Some message

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os
import yaml
from voluptuous import Schema, Optional

from ..util import autolog

class KitException(BaseException):
    """Basic Kit exception"""
    pass

class Kit:
    """
    Kit base class

    A kit is basically a generic service configuration
    schema with both variable and template files targeting
    a specific service (e.g. i3wm).

    Kits can be either accessed locally or from the internet using git
    and are capable of rendering one or more target files (e.g. a gtk kit
    could target both configurations for gtk2 and gtk3).

    Kits are basically file systems with the following layout:

    * /kit_directory
    |
    |__* /templates <-------- Templates base layout
    | |__ /base <------------ This is a template package
    |    |__ main.j2
    |    |__ (*.j2)
    | |__ /another_one <----- This is another one
    |    |__ main.j2
    |    |__ (*.j2)
    |__* /defaults <---------- Template default variables directory
    |   |__ varfile.yml
    |   |__ hello.yml
    |   |__ (*.yml)
    |__ * index.yml <-------- Index(description) file
    """

    def __init__(self, name, *, root_dir):
        """
        Constructor

        :param name: kit name
        :param root_dir: full path to the kit
        """

        # Get the very basic information
        self._name = name
        self._root_dir = root_dir

        # Validate file system
        self._check_filesystem(self._root_dir, self._name)

        # Kits are compelled to have a certain file system:
        # > 2 directories:
        #  * 'defaults': all variables used by the kit must
        #     be defined in YAML files inside this directory
        #  * 'templates': all templates must be in this directory
        # > An index file: index.yml
        #   This file holds key metadata used to define basic information
        #   and template definitions as well.
        self._index_file = "{}/index.yml".format(self._root_dir)

        #####################################################
        # Index files from kits must obey a schema as follows
        #####################################################
        schema = Schema({
            # Kit author name
            'author': str,

            # Kit unique name
            'name': str,

            # Kit version
            # TODO: Implement semantic version
            'version': str,

            # Kit general description
            Optional('description'): str,

            # Kit license
            Optional('license'): str,

            ########################################
            # Description of all templates specified
            # in this kit. This entry must be a dictionary:
            # * Each key must correspond to a template directory inside
            #   the 'templates' directory of the kit
            # * Each entry is also a dictionary whose keys
            #   must be the following.
            #   > output_file: path to the template output file,
            #     must be relative to the user home directory.
            ########################################
            'templates': dict,  # TODO: temporary
        }, required=True)

        # Attempt to open the index file:
        with open(self._index_file, 'r') as file:
            self._index_data = schema(yaml.load(file))

        ###################################################
        # All templates have their base templates directory
        # as their include path, in this way, templates can include
        # other ones from inside the kit
        ###################################################
        template_default_include = os.path.join(self._root_dir, 'templates')

        ################################################################
        # Templates must be confined within their own directories
        # inside templates directory, per template, there are individual
        # settings, such as the output file. A kit can have several templates
        # thus can output as many files as templates it has.
        ################################################################
        self._templates = self._index_data['templates']

        ###################################################
        # Explore each template specified in the index file
        ###################################################
        for template in self._templates.keys():
            # Per template, base templates directory is set as one of its
            # include directories
            template_include = os.path.join(template_default_include, template)

            # On each template directory inside 'templates', there must
            # be at least a jinja template file named main.j2, which is
            # treated as the entry point for each template directory
            self._templates[template]['path'] = '{}/main.j2'.format(template)

            # These are the include directories used by the rendered when
            # rendering main.j2 with jinja2
            self._templates[template]['include'] = [
                template_include, template_default_include
            ]

            # Each template must have a specified output file
            template_output_file = self._templates[template]['output_file']

        # Set variable directories for this kit
        # Each kit can have default variables than can base used
        # all across its templates, these can be defined within
        # YAML files within its 'defaults' directory
        self._var_dirs = os.path.join(self._root_dir, 'defaults')

    @property
    def index_data(self):
        return self._index_data

    @property
    def index_file(self):
        return self._index_file

    @property
    def root_dir(self):
        """Kit base directory"""
        return self._root_dir

    @property
    def var_dir(self):
        """Kit variables directory"""
        return self._var_dirs

    @property
    def templates(self):
        """Kit templates descriptions"""
        return self._templates

    @staticmethod
    def _check_filesystem(root_dir, kit_name):
        """Check whether this kit is actually a valid one"""
        if not os.path.isdir(root_dir):
            raise KitException("Kit '{}' doesn't have a valid base directory".format(kit_name))
        if not os.path.isdir("{}/templates".format(root_dir)):
            raise KitException("Kit '{}' must have a templates directory".format(kit_name))
        if not os.path.isdir("{}/defaults".format(root_dir)):
            raise KitException("Kit '{}' must have a defaults directory".format(kit_name))
