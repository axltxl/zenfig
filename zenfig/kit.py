# -*- coding: utf-8 -*-

"""
zenfig.kit
~~~~~~~~

Kit interface

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os

import git
from git.exc import InvalidGitRepositoryError

from . import log
from . import util

#
GIT_REPO = "https://github.com/axltxl/zenfig-kits.git"
GIT_REF  = "refs/heads/dunst" # temporary

#
KIT_CACHE_HOME = "{}/kits".format(util.get_xdg_cache_home())

def _get_kits_root_dir():
    return "{}/zenfig/kits".format(util.get_xdg_cache_home())

def _get_kit_dir(kit_name):
    return "{}/{}".format(KIT_CACHE_HOME, kit_name)

def _kit_exists(kit_name):
    return os.path.exists(_get_kit_dir(kit_name))

def get_var_dir(kit):
    """TODO: Docstring for get_var_dir.

    :kit: TODO
    :returns: TODO

    """
    # Give back XDG_CACHE_HOME/zenfig/kits/<kit>/defaults
    # if existent, otherwise, give None
    if _kit_exists(kit_name):
        return "{}/defaults".format(_get_kit_dir(kit_name))
    return None

def _create_cache():
    # Clean everything first
    if os.path.exists(KIT_CACHE_HOME):
        os.removedirs(KIT_CACHE_HOME)

    #
    log.msg_debug("Creating kit cache at '{}'".format(KIT_CACHE_HOME))
    os.makedirs(KIT_CACHE_HOME)

    # clone the thing
    log.msg_warn("Cloning kits repository")
    git_repo = git.Repo.clone_from(
        url=GIT_REPO,
        to_path=KIT_CACHE_HOME,
        depth=1
    )
    log.msg_warn("Done!")

    return git_repo

def update_cache():

    log.msg("Updating kits cache ...")
    # check for git repo at XDG_CACHE_HOME/zenfig/kits
    # if directory not present, clone the repo with depth=1
    if not os.path.exists(KIT_CACHE_HOME):
        git_repo = _create_cache()
    else:
        try:
            #TODO: implement this
            git_repo = git.Repo(
                KIT_CACHE_HOME,
                branch_path=GIT_REF
                )
            # otherwise, pull from it
            git_repo.pull(refspec=GIT_REF)
        except InvalidGitRepositoryError:
            git_repo = _create_cache()


def get_template_dir(kit_name):
    """TODO: Docstring for get_template_dir.

    :kit_name: TODO
    :returns: TODO

    """
    pass

    #TODO: implement this!
    # if kit exists inside git_repo
    if _kit_exists(kit_name):
        return "{}/templates".format(_get_kit_dir(kit_name))
    # return string XDG_CACHE_HOME/zenfig/kits/<kit>
    # else return None
    return None
