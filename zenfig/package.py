# -*- coding: utf-8 -*-

"""
zenfig.package
~~~~~~~~

Package interface

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

#
GIT_REPO = "https://github.com/axltxl/zenfig-packages.git"

def _get_packages_root_dir():
    return "{}/zenfig/packages".format(util.get_xdg_cache_home())

def get_var_dir(package):
    """TODO: Docstring for get_var_dir.

    :package: TODO
    :returns: TODO

    """
    # Give back XDG_CACHE_HOME/zenfig/packages/<package>/defaults
    # if existent, otherwise, give None
    pass

def update_cache(package):
    #TODO: implement this
    # check for git repo at XDG_CACHE_HOME/zenfig/packages
    # if directory not present, clone the repo with depth=1

    # otherwise, pull from it
    pass

def get_template_dir(package):
    """TODO: Docstring for get_template_dir.

    :package: TODO
    :returns: TODO

    """
    pass

    #TODO: implement this!
    # if package exists inside git_repo
    # return string XDG_CACHE_HOME/zenfig/packages/<package>
    # else return None
