# -*- coding: utf-8 -*-

"""
zenfig.kits.git
~~~~~~~~

Git kit interface

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

import os
import shutil
import re
from time import time
from base64 import standard_b64encode

import git
from git.exc import InvalidGitRepositoryError
from git.exc import GitCommandError

from . import Kit, KitException

from .. import log
from .. import util
from ..util import autolog

class GitRepoKit(Kit):
    """Kit as git repository"""

    # Regular expression for catching git repositories
    RE_GIT_REPO_SHORT = "^[a-zA-Z0-9\-_]+\/[a-zA-Z0-9\-_]+(==[a-zA-Z0-9-_.]+)?$"
    RE_GIT_REPO_URL = "^http.*\.git+(==[a-zA-Z0-9-_.]+)?$"

    # Essential git repo variables
    GIT_REPO_PREFIX_DEFAULT = "https://github.com"

    # Git reference type to use
    GIT_REF_TAG = 1
    GIT_REF_HEAD = 2

    # Kit cache location
    CACHE_HOME = "{}/kits".format(util.get_xdg_cache_home())

    # Kit cache maximum allowed modification time in cache
    CACHE_MAX_TIME = 259200  # 3 days

    def __init__(self, kit_name, *, version=None):
        """ Constructor """

        # Kit version requested by user
        self._version = version

        # Determine kit version, which is in this
        # base the name of the branch to be pulled
        # or checked out depending on the case.
        if self._version is None:
            self._version = 'master'

        # Kit repository essentials
        self._git_repo = None
        self._git_repo_name, self._git_repo_url = self._get_repo_name(kit_name)
        self._git_repo_path = self._get_kit_dir(self._git_repo_name)


        # These are used for git operations on local kit cache
        self._git_remote = None
        self._git_ref = None
        self._git_ref_type = None

        try:
            # Proceed to update local kit cache
            self._cache_update(kit_name)

            # Call my parent
            super().__init__(kit_name, root_dir=self._git_repo_path)

        except KitException as kit_except:

            # Destroy kit if invalid
            if not self._cache_isvalid():
                self._cache_destroy_kit()
            raise kit_except

    def _get_repo_name(self, kit_name):
        """Generate repo name and its URL"""

        if not re.match(self.RE_GIT_REPO_URL, kit_name):
            # We asume <user_name>/<repo_name> came by
            git_repo_prefix, git_repo_name = kit_name.split('/')
            git_repo_url = "{}/{}/{}.git".format(
                self.GIT_REPO_PREFIX_DEFAULT,
                git_repo_prefix, git_repo_name
            )
            return (kit_name, git_repo_url)
        return (
            # Should received kit_name be a plain URL, its name would be
            # its encoded form (into base64)
            standard_b64encode(kit_name.encode('ascii')).decode('utf-8'),
            kit_name
        )

    def _cache_update(self, kit_name):
        """Update kit cache"""

        try:
            #####################################
            # First of all, perform sanity checks
            # on self.CACHE_HOME
            #####################################

            # Create new local cache at self.CACHE_HOME
            if not self._cache_isvalid():
                self._git_repo = self._cache_create_kit()

            else:

                # get current kit git repo
                self._git_repo = git.Repo(self._git_repo_path)

                # log the thing
                log.msg_debug("Updating kit: {}@{}".format(kit_name, self._version))


            # This kit provider deals with remote refs from 'origin'
            # directly, namely, it locates them and checks them out
            # for further use by zenfig

            # 'origin' is used as the remote
            self._git_remote = self._git_repo.remotes.origin

            # Determine whether self._version is either a
            # branch or a tag reference
            if self._version in self._git_remote.refs:
                self._git_ref_type = self.GIT_REF_HEAD
                self._git_ref = self._git_remote.refs[self._version]
            elif self._version in self._git_repo.tags:
                self._git_ref_type = self.GIT_REF_TAG
                self._git_ref = self._git_repo.tags[self._version]
            else:
                raise KitException(
                    "Ref '{}' not found on git repository".format(self._version)
                )

            # Pull latest changes from the remote repo
            self._cache_kit_pull()

            #################################################
            # Proceed to actual checkout of the specified ref
            #################################################
            try:
                if self._git_ref_type == self.GIT_REF_TAG:
                    self._git_ref.ref.checkout(force=True)
                self._git_ref.checkout(force=True)
            except TypeError:
                # Dealing with remote references on GitPython
                # raises TypeError exceptions, which in this case,
                # are irrelevant
                pass

        except InvalidGitRepositoryError:
            ################################################
            # At this point, most likely, the local cache
            # has been corrupted, therefore, it is necessary
            # to do the thing all over
            ################################################
            log.msg_warn(
                "[{}] Invalid git repo found on cache, rebuilding it ..."
                .format(kit_name)
            )
            self._cache_create_kit()
            self._cache_update(kit_name)

    def _cache_create_kit(self):
        """
        Construct kit cache

        :returns: A cloned git repository
        """

        # Clean everything first
        self._cache_destroy_kit()

        # Proceed to create entire kit cache file system
        # which is located at XDG_self.CACHE_HOME/zenfig/kits
        log.msg_debug("Creating local kit cache at '{}'".format(self._git_repo_path))
        os.makedirs(self._git_repo_path)

        ########################################################
        # Clone the kit repository
        # kit repos can be specified as <user_name>/<repo_name>.
        # For the moment, only github repos will be looked up on this provider
        # That is, unless, you specify an URL
        ########################################################

        # give back the cloned git repository
        return self._clone_repo()

    def _clone_repo(self):
        try:
            log.msg_warn("Cloning kit repository: {}".format(self._git_repo_url))
            return git.Repo.clone_from(
                url=self._git_repo_url,
                to_path=self._git_repo_path,
            )
        except:
            raise KitException(
                "Unable to clone kit repository at {}"
                .format(self._git_repo_url)
            )

    def _cache_isvalid(self):
        """Tell whether the local cache is valid"""

        # does the cache actually exist?
        if not os.path.exists(self._git_repo_path):
            log.msg_err(
                "Kit cache for '{}' does not exist"
                .format(self._git_repo_name)
            )
            return False

        # is it an actual directory?
        if not os.path.isdir(self._git_repo_path) or \
        os.path.islink(self._git_repo_path):
            log.msg_err(
                "Kit cache for '{}' is not a valid directory!"
                .format(self._git_repo_name)
            )

        # OK, it's good to go!
        return True

    def _cache_is_too_old(self):
        """Tell whether a git repository for kit_name is too old"""

        ################################################
        # base on directory's modification time
        # tell whether or not this kit should be updated
        ################################################
        return os.path.getmtime(
            self._git_repo_path) < (time() - self.CACHE_MAX_TIME
        )

    def _cache_kit_pull(self):
        """Pull latest changes from the remote repo"""

        if self._cache_is_too_old():
            self._git_remote.pull(refspec=self._git_ref)

    def _cache_destroy_kit(self):
        """Destroy kit in cache"""

        if os.path.exists(self._git_repo_path):
            log.msg_warn(
                "Wiping kit cache ({}) ..."
                .format(self._git_repo_path)
            )
            shutil.rmtree(self._git_repo_path)

    def _get_kit_dir(self, kit_name):
        return os.path.join(self.CACHE_HOME, kit_name)


@autolog
def get_kit(kit_name, kit_version):
    """Initialise kit provider"""

    return GitRepoKit(kit_name, version=kit_version)
