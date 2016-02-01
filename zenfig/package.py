# -*- coding: utf-8 -*-

"""
zenfig.package
~~~~~~~~

Package interface

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os

import git
from git.exc import InvalidGitRepositoryError

from . import log
from . import util

#
GIT_REPO = "https://github.com/axltxl/zenfig-packages.git"
GIT_REF  = "refs/heads/dunst" # temporary

#
PACKAGE_CACHE_HOME = "{}/packages".format(util.get_xdg_cache_home())

def _get_packages_root_dir():
    return "{}/zenfig/packages".format(util.get_xdg_cache_home())

def _get_package_dir(package_name):
    return "{}/{}".format(PACKAGE_CACHE_HOME, package_name)

def _package_exists(package_name):
    return os.path.exists(_get_package_dir(package_name))

def get_var_dir(package):
    """TODO: Docstring for get_var_dir.

    :package: TODO
    :returns: TODO

    """
    # Give back XDG_CACHE_HOME/zenfig/packages/<package>/defaults
    # if existent, otherwise, give None
    if _package_exists(package_name):
        return "{}/defaults".format(_get_package_dir(package_name))
    return None

def _create_cache():
    # Clean everything first
    if os.path.exists(PACKAGE_CACHE_HOME):
        os.removedirs(PACKAGE_CACHE_HOME)

    #
    log.msg_debug("Creating package cache at '{}'".format(PACKAGE_CACHE_HOME))
    os.makedirs(PACKAGE_CACHE_HOME)

    # clone the thing
    log.msg_warn("Cloning packages repository")
    git_repo = git.Repo.clone_from(
        url=GIT_REPO,
        to_path=PACKAGE_CACHE_HOME,
        depth=1
    )
    log.msg_warn("Done!")

    return git_repo

def update_cache():

    log.msg("Updating packages cache ...")
    # check for git repo at XDG_CACHE_HOME/zenfig/packages
    # if directory not present, clone the repo with depth=1
    if not os.path.exists(PACKAGE_CACHE_HOME):
        git_repo = _create_cache()
    else:
        try:
            #TODO: implement this
            git_repo = git.Repo(
                PACKAGE_CACHE_HOME,
                branch_path=GIT_REF
                )
            # otherwise, pull from it
            git_repo.pull(refspec=GIT_REF)
        except InvalidGitRepositoryError:
            git_repo = _create_cache()


def get_template_dir(package_name):
    """TODO: Docstring for get_template_dir.

    :package_name: TODO
    :returns: TODO

    """
    pass

    #TODO: implement this!
    # if package exists inside git_repo
    if _package_exists(package_name):
        return "{}/templates".format(_get_package_dir(package_name))
    # return string XDG_CACHE_HOME/zenfig/packages/<package>
    # else return None
    return None
