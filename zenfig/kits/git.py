
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
from ..util import autolog

from . import __kit_isvalid

# Essential git repo variables
GIT_REPO = "https://github.com/axltxl/zenfig-kits.git"
GIT_BRANCH = "master"
GIT_REF  = "refs/heads/{}".format(GIT_BRANCH)

# Kit cache location
KIT_CACHE_HOME = "{}/kits".format(util.get_xdg_cache_home())

# Kit cache maximum allowed size
KIT_CACHE_MAX_SIZE = 20480


@autolog
def _cache_create():
    """
    Construct kit cache

    :returns: A cloned git repository
    """

    # Clean everything first
    if os.path.exists(KIT_CACHE_HOME):
        log.msg_warn("Wiping kit cache ...")
        os.removedirs(KIT_CACHE_HOME)

    # Proceed to create entire kit cache file system
    # which is located at XDG_CACHE_HOME/zenfig/kits
    log.msg_debug("Creating kit cache at '{}'".format(KIT_CACHE_HOME))
    os.makedirs(KIT_CACHE_HOME)

    ##########################
    # Clone the kit repository
    ##########################
    log.msg_warn("Cloning kit repository")
    git_repo = git.Repo.clone_from(
        url=GIT_REPO,
        to_path=KIT_CACHE_HOME,
        depth=1,
        branch=GIT_BRANCH
    )

    # give back the cloned git repository
    return git_repo

@autolog
def _cache_isvalid():
    """Tell whether the local cache is valid"""

    # does the cache actually exist?
    if not os.path.exists(KIT_CACHE_HOME):
        log.msg_err("Kit cache does not exist")
        return False

    # is it an actual directory?
    if not os.path.isdir(KIT_CACHE_HOME) or \
    os.path.islink(KIT_CACHE_HOME):
        log.msg_err("Kit cache is not a valid directory!")

    # is it taking too much of your hard drive?
    # kit_cache_size = os.path.getsize(KIT_CACHE_HOME)
    kit_cache_size = sum([os.path.getsize(f) for f in os.listdir(KIT_CACHE_HOME) if os.path.isfile(f)])
    log.msg_debug("Kit cache size: {:.2f} MiB".format(kit_cache_size/1024))
    if kit_cache_size > KIT_CACHE_MAX_SIZE:
        log.msg_warn("Kit cache is taking more "\
            "space than it should ({})".format(kit_cache_size))
        return False

    # OK, it's good to go!
    return True


@autolog
def _cache_update():
    """Update kit cache"""

    # log the thing
    log.msg_debug("Updating kits cache ...")

    #####################################
    # First of all, perform sanity checks
    # on KIT_CACHE_HOME
    #####################################
    if not _cache_isvalid():
        # Create new local cache at KIT_CACHE_HOME
        git_repo = _cache_create()
    else:
        try:
            # get current kit cache
            git_repo = git.Repo(KIT_CACHE_HOME)

            # Pull latest changes from the remote repo
            log.msg_debug("Pulling from repo")
            git_remote = git_repo.remotes.origin
            git_remote.pull(refspec=GIT_REF)

        except InvalidGitRepositoryError:
            ################################################
            # At this point, most likely, the local cache
            # has been corrupted, therefore, it is necessary
            # to do the thing all over
            ################################################
            log.msg_warn("Invalid git repo found on cache, rebuilding it ...")
            git_repo = _cache_create()

    # Make sure the repo is at the right branch
    # reset any changes checkout to GIT_BRANCH
    for head in git_repo.heads:
        if head.name == GIT_BRANCH:
            head.checkout(force=True)

@autolog
def _get_kit_dir(kit_name):
    return "{}/{}".format(KIT_CACHE_HOME, kit_name)

@autolog
def init():
    """Initialise kit provider"""
    _cache_update()

@autolog
def kit_isvalid(kit_name):
    return __kit_isvalid(_get_kit_dir(kit_name))

@autolog
def get_template_dir(kit_name):
    return "{}/templates".format(_get_kit_dir(kit_name))

@autolog
def get_var_dir(kit_name):
    return "{}/defaults".format(_get_kit_dir(kit_name))

