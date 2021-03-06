# -*- coding: utf-8 -*-

"""
zenfig.depgraph.node
~~~~~~~~

Node implementation

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""


from . import DepGraphException

class Node:
    """
    Graph node implementation
    """

    def __init__(self, key, value, *, depgraph):
        """
        Constructor

        :param key: This node's unique name
        :param value: This node's value
        :param depgraph: Owner DepGraph of this node
        """

        # Set the basics, first
        self._key = key
        self._value = value
        self._depgraph = depgraph

        # Whether or not this variable has been already evaluated
        self._evaluated = False

        # Dependencies of this node:
        # This is a dict containing all nodes this node
        # depends on before its value can be evaluated
        self._deps = {}

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def deps(self):
        return self._deps

    @deps.setter
    def deps(self, value):
        self._deps = value

    def calc_deps(self):
        """
        Calculate dependencies for this node

        Each node is responsible for finding out its own dependencies
        This node's parent DepGraph will call this method at graph construction
        time, thus, it must be superseeded by any child implementation of
        this class in order to really do something.

        :returns: a list of all keys of nodes this node depends on
        """

        return []

    def get_node(self, key):
        """
        Get access to any node within this node's parent DepGraph

        :param key: node key
        :returns: a Node instance
        """

        return self._depgraph.get_node(key)

    def on_evaluate(self):
        """
        Evaluate this node

        Each node is responsible for its own evaluation,
        it should use all info provided by its DepGraph in
        order to settle down its value. This method is indirectly
        called by its parent DepGraph evaluate() method.
        """

        raise NotImplementedError("You must implement this method")

    def evaluate(self, *seen):
        """
        Evaluate this node (the real implementation)

        This method is called by this node's parent DepGraph
        at evaluation time. It basically manages to resolve
        all dependencies for then settle down this node's value.
        """

        # First of all, before a node's value can be evaluated,
        # its dependencies HAVE to be evaluated first
        for dep_name, dep_node in self._deps.items():
            # at some point during dependencies evaluation, one
            # of them could be already have been evaluated, meaning
            # one thing: circular dependency.
            if dep_name in seen:
                raise DepGraphException(self._fmt_msg_circ_dep(dep_name, seen))

            # If everything is good, put this dependency on the
            # tracked ones list
            seen += (dep_name,)

            # Actually evaluate this dependency
            dep_node.evaluate(*seen)

        # Don't even bother to evaluate this node if it's been
        # already evaluated.
        if not self._evaluated:

            # Mark this node as evaluated
            self._evaluated = True

            # Now that all dependencies have been evaluated,
            # proceed to evaluate this node itself.
            self.value = self.on_evaluate()

        # Finally, give back this node's value
        return self.value

    @staticmethod
    def _fmt_msg_circ_dep(dep_name, seen):
        msg_err = "Circular dependency detected! "
        for dep in seen:
            msg_err += "{} ~> ".format(dep)
        msg_err += dep_name
        return msg_err
