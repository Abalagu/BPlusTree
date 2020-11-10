# Created by Luming on 11/10/2020 1:47 PM
from math import ceil, floor
from typing import Optional, List, Dict

from enum import Enum


class NodeType(Enum):
    NON_LEAF = 'non_leaf',
    LEAF = 'leaf',
    ROOT = 'root',
    NONE = None,


class Node:
    def __init__(self, node_type=NodeType.NONE, keys=None, pointers=None):
        """sequence pointer only works when node type is LEAF"""
        self.node_type: NodeType = node_type
        self.keys: List[int] = keys if keys is not None else []
        self.pointers: List[Node] = pointers if pointers is not None else []
        self.sequence_pointer: Optional[Node] = None

    def __str__(self):
        return "{} node, {} keys, {} pointers".format(self.node_type, len(self.keys), len(self.pointers))


def gen_constraint(order: int):
    """generate b plus tree node attribute constraint. ref: note17 p3"""
    constraint = {
        NodeType.NON_LEAF: {
            'max_pointers': order + 1,
            'max_keys': order,
            'min_pointers': ceil((order + 1) / 2),
            'min_keys': ceil((order + 1) / 2) - 1,
        },
        NodeType.LEAF: {
            'max_pointers': order + 1,
            'max_keys': order,
            'min_pointers': floor((order + 1) / 2) + 1,
            'min_keys': floor((order + 1) / 2),
        },
        NodeType.ROOT: {
            'max_pointers': order + 1,
            'max_keys': order,
            'min_pointers': 2,
            'min_keys': 1,
        }
    }
    return constraint


class BPlusTree:
    """construct a tree with empty root node, or with a given root"""

    def __init__(self, order: int, root: Node = None):
        self.order: int = order
        self.root: Node = Node(NodeType.ROOT) if root is None else root
        self.constraint: Dict = gen_constraint(self.order)

    def met_constraint(self, node: Node) -> bool:
        """perform constraint check for the given node and all its child nodes """
        if node.node_type is NodeType.NONE:  # cannot check node constraint without type
            print("node type not specified")
            return True

        constr = self.constraint[node.node_type]
        if len(node.keys) < constr['min_keys'] or len(node.keys) > constr['max_keys'] \
                or len(node.pointers) < constr['min_pointers'] or len(node.pointers) > constr['max_pointers']:
            print("expect: [{}, {}] keys, [{}, {}] pointers; actual: {}"
                  .format(constr['min_keys'], constr['max_keys'],
                          constr['min_pointers'], constr['max_pointers'], str(node)))
            return False

        for child in node.pointers:
            if not self.met_constraint(child):
                return False
        else:
            return True
