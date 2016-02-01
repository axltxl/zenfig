
"""
zenfig.kits.git
~~~~~~~~

Git kit interface?

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os

import git
from git.exc import InvalidGitRepositoryError

from .. import log
from .. import util

#
GIT_REPO = "https://github.com/axltxl/zenfig-kits.git"
GIT_REF  = "refs/heads/dunst" # temporary

#
KIT_CACHE_HOME = "{}/kits".format(util.get_xdg_cache_home())


def _cache_create():
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

def _cache_update():

    log.msg("Updating kits cache ...")
    # check for git repo at XDG_CACHE_HOME/zenfig/kits
    # if directory not present, clone the repo with depth=1
    if not os.path.exists(KIT_CACHE_HOME):
        git_repo = _cache_create()
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
            git_repo = _cache_create()

def _get_kit_dir(kit_name):
    return "{}/{}".format(KIT_CACHE_HOME, kit_name)

def init():
    _cache_update()

def kit_exists(kit_name):
    kit_dir = _get_kit_dir(kit_name)
    if not os.isdir(kit_dir):
        return False
    if not os.isdir("{}/templates".format(kit_dir)):
        return False
    if not os.isdir("{}/defaults".format(kit_dir)):
        return False
    return True

def get_template_dir(kit_name):
    return "{}/templates".format(_get_kit_dir(kit_name))

def get_var_dir(kit):
    return "{}/defaults".format(_get_kit_dir(kit_name))

