# -*- coding: utf-8 -*-

"""
zenfig.kits.git
~~~~~~~~

Git kit interface

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os
from time import time

import git
from git.exc import InvalidGitRepositoryError
from git.exc import GitCommandError

from .. import log
from .. import util
from ..util import autolog

from . import __kit_isvalid

# Essential git repo variables
#TODO: if kit_name comes as an URL, don't use this
GIT_REPO_PREFIX_DEFAULT = "https://github.com"
GIT_BRANCH = "master"
GIT_REF  = "refs/heads/{}".format(GIT_BRANCH)

# Kit cache location
KIT_CACHE_HOME = "{}/kits".format(util.get_xdg_cache_home())

# Kit cache maximum allowed size
KIT_CACHE_MAX_SIZE = 2048  # 2 megs
KIT_CACHE_MAX_TIME = 259200  # 3 days

@autolog
def _cache_create(kit_name):
    """
    Construct kit cache

    :returns: A cloned git repository
    """

    # Get git repository path
    git_repo_path = _get_kit_dir(kit_name)

    # Clean everything first
    if os.path.exists(git_repo_path):
        log.msg_warn("Wiping kit cache ...")
        os.removedirs(git_repo_path)

    # Proceed to create entire kit cache file system
    # which is located at XDG_CACHE_HOME/zenfig/kits
    log.msg_debug("Creating kit cache at '{}'".format(git_repo_path))
    os.makedirs(git_repo_path)

    ########################################################
    # Clone the kit repository
    # kit repos can be specified as <user_name>/<repo_name>.
    # For the moment, only github repos will be looked up on this provider
    ########################################################
    git_repo_prefix, git_repo_name = kit_name.split('/')
    try:
        # try zenfig- prefix on git repo, first
        git_repo_remote = "{}/{}/zenfig-{}.git".format(
            GIT_REPO_PREFIX_DEFAULT, git_repo_prefix, git_repo_name
        )
        git_repo = _clone_repo(git_repo_remote, git_repo_path)
    except GitCommandError:
        git_repo_remote = "{}/{}/{}.git".format(
            GIT_REPO_PREFIX_DEFAULT, git_repo_prefix, git_repo_name
        )
        git_repo = _clone_repo(git_repo_remote)

    # give back the cloned git repository
    return git_repo

@autolog
def _clone_repo(git_repo_remote, git_repo_path):
    log.msg_warn("Cloning kit repository: {}".format(git_repo_remote))
    return git.Repo.clone_from(
        url=git_repo_remote,
        to_path=git_repo_path,
        depth=1,
        branch=GIT_BRANCH
    )

@autolog
def _cache_isvalid(kit_name):
    """Tell whether the local cache is valid"""

    # Get git repository path
    git_repo_path = _get_kit_dir(kit_name)

    # does the cache actually exist?
    if not os.path.exists(git_repo_path):
        log.msg_err("Kit cache does not exist")
        return False

    # is it an actual directory?
    if not os.path.isdir(git_repo_path) or \
    os.path.islink(git_repo_path):
        log.msg_err("Kit cache is not a valid directory!")

    # is it taking too much of your hard drive?
    # kit_cache_size = os.path.getsize(KIT_CACHE_HOME)
    kit_cache_size = sum([os.path.getsize(f) for f in os.listdir(git_repo_path) if os.path.isfile(f)])
    log.msg_debug("Kit cache size: {:.2f} MiB".format(kit_cache_size/1024))
    if kit_cache_size > KIT_CACHE_MAX_SIZE:
        log.msg_warn("Kit cache is taking more "\
            "space than it should ({})".format(kit_cache_size))
        return False

    # OK, it's good to go!
    return True

@autolog
def _cache_is_too_old(kit_name):
    """Tell whether a git repository for kit_name is too old"""

    ################################################
    # base on directory's modification time
    # tell whether or not this kit should be updated
    ################################################
    return os.path.getmtime(
        _get_kit_dir(kit_name)) < (time() - KIT_CACHE_MAX_TIME
    )

@autolog
def _cache_update(kit_name):
    """Update kit cache"""

    #####################################
    # First of all, perform sanity checks
    # on KIT_CACHE_HOME
    #####################################
    if not _cache_isvalid(kit_name):
        # Create new local cache at KIT_CACHE_HOME
        git_repo = _cache_create(kit_name)
    else:
        try:
            # Check whether cache is not too old
            if not _cache_is_too_old(kit_name):
                return

            # get full path to local copy of the kit
            # (local git repository)
            git_repo_path = _get_kit_dir(kit_name)

            # get current kit cache
            git_repo = git.Repo(git_repo_path)

            # log the thing
            log.msg_debug("Updating kit: {}".format(kit_name))

            # Pull latest changes from the remote repo
            git_remote = git_repo.remotes.origin
            git_remote.pull(refspec=GIT_REF)

        except InvalidGitRepositoryError:
            ################################################
            # At this point, most likely, the local cache
            # has been corrupted, therefore, it is necessary
            # to do the thing all over
            ################################################
            log.msg_warn("Invalid git repo found on cache, rebuilding it ...")
            git_repo = _cache_create(kit_name)

    # Make sure the repo is at the right branch
    # reset any changes checkout to GIT_BRANCH
    for head in git_repo.heads:
        if head.name == GIT_BRANCH:
            head.checkout(force=True)

@autolog
def _get_kit_dir(kit_name):
    return "{}/{}".format(KIT_CACHE_HOME, kit_name)

@autolog
def init(kit_name):
    """Initialise kit provider"""
    _cache_update(kit_name)

@autolog
def kit_isvalid(kit_name):
    return __kit_isvalid(_get_kit_dir(kit_name))

@autolog
def get_template_dir(kit_name):
    return "{}/templates".format(_get_kit_dir(kit_name))

@autolog
def get_var_dir(kit_name):
    return "{}/defaults".format(_get_kit_dir(kit_name))

