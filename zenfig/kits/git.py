
"""
zenfig.kits.git
~~~~~~~~

Git kit interface

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os

import git
from git.exc import InvalidGitRepositoryError

from .. import log
from .. import util

from . import __kit_isvalid

#
GIT_REPO = "https://github.com/axltxl/zenfig-kits.git"
GIT_BRANCH = "dunst"
GIT_REF  = "refs/heads/{}".format(GIT_BRANCH) # temporary

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
        depth=1,
        branch=GIT_BRANCH
    )

    #
    return git_repo

def _cache_update():

    #
    log.msg_debug("Updating kits cache ...")

    #
    if not os.path.exists(KIT_CACHE_HOME):
        git_repo = _cache_create()
    else:
        try:
            #TODO: implement this
            git_repo = git.Repo(KIT_CACHE_HOME)

            # otherwise, pull from it
            log.msg_debug("Pulling from repo")
            git_remote = git_repo.remotes.origin
            git_remote.pull(refspec=GIT_REF)

        except InvalidGitRepositoryError:
            log.msg_warn("Invalid git repo found on cache, rebuilding it ...")
            git_repo = _cache_create()

    # make sure the repo is at the right branch
    # reset any changes
    # checkout to GIT_BRANCH
    for head in git_repo.heads:
        if head.name == GIT_BRANCH:
            log.msg_warn("reseting git repo")
            head.checkout(force=True)

def _get_kit_dir(kit_name):
    return "{}/{}".format(KIT_CACHE_HOME, kit_name)

def init():
    _cache_update()

def kit_isvalid(kit_name):
    return __kit_isvalid(_get_kit_dir(kit_name))

def get_template_dir(kit_name):
    return "{}/templates".format(_get_kit_dir(kit_name))

def get_var_dir(kit_name):
    return "{}/defaults".format(_get_kit_dir(kit_name))

