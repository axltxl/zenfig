# -*- coding: utf-8 -*-

"""
zenfig.depgraph.depgraph
~~~~~~~~

Dependency graph implementation

:copyright: (c) 2016 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

from .. import log
from .node import Node



class DepGraph:
    """
    Dependency Graph implementation

    This is a basic data structure for tracking down
    nodes and their dependencies and methods to evaluate
    and therefore resolve their values according to dependency
    relationships among nodes.
    """

    def __init__(self, node_class=Node, **kwargs):
        """
        Constructor

        Create a new dependency graph from a bunch of arbitrary
        keyword arguments. Each one of them become an instance of
        node_class.

        :param node_class: Class used to instantiate nodes within the graph
        :param kwargs: Arbitrary keyword arguments
        """

        # node_class must be a subclass of Node
        if not issubclass(node_class, Node):
            raise TypeError("node_class must be derived from Node")

        # Create nodes from arbitrary keyword arguments
        self._nodes = {}
        for key, value in kwargs.items():
            self._nodes[key] = node_class(key, value, depgraph=self)

        # After all nodes have been registered,
        # create dependency relationships among them
        for node in self._nodes.values():
            for dep in set(node.calc_deps()):
                if dep in self._nodes:
                    node.deps[dep] = self._nodes[dep]
                else:
                    # Insert an artificial node with a null value:
                    # This means this node is depending on a variables
                    # that hasn't been defined in any way or any variable file.
                    # Normally, this would be enough reason to trigger an exception,
                    # but the thing is that it is simply obnoxious for the user,
                    # so instead, a warning is raised and a node whose value is
                    # an empty string is inserted.
                    log.msg_warn("'{}' is required by '{}' but it is not defined anywhere!.".format(dep, node.key))
                    node.deps[dep] = node_class(dep, "{}_NotImplemented".format(dep), depgraph=self)

        # A dictionnary containing all resolved variables
        # from this graph after they have been evaluated
        self._resolved = {}

    def get_node(self, key):
        """
        Get a specific node from this graph

        :param key: Name of the node to retrieve
        :returns: a Node instance if found, otherwise None
        """

        try:
            return self._nodes[key]
        except KeyError:
            return None

    def evaluate(self):
        """
        Evaluate all nodes within this graph

        Once the graph has been constructed, including
        its nodes and dependencies, nodes can then be
        "evaluated", namely, their values can be settled
        in relationship with what their values and dependencies
        have.

        :returns: A dictionary containing all nodes' values
        """

        # One by one, all nodes are evaluated individually
        for key, node in self._nodes.items():
            # node.evaluate()
            # self._resolved[key] = node.value
            self._resolved[key] = node.evaluate()

        # Give that thing already!
        return self._resolved
