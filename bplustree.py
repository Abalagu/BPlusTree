# Created by Luming on 11/10/2020 1:47 PM
from enum import Enum
from math import ceil, floor
from typing import Optional, List, Dict, Any


class NodeType(Enum):
    NON_LEAF = 'non_leaf',
    LEAF = 'leaf',
    ROOT = 'root',
    NONE = None,


class Node:
    def __init__(self, keys=None, pointers=None, payload: List[Any] = None, node_type=NodeType.NONE):
        """sequence pointer only works when node type is LEAF
        a node represents a square with multiple values and pointers.

        pointers: in leaf node the list is always empty; in
                  in non-leaf node the list points to child nodes

        Leaf node: key,
        """
        self.node_type: NodeType = node_type
        self.keys: List[int] = keys if keys else []
        self.pointers: List[Node] = pointers if pointers else []
        self.payload: List[Any] = payload if payload else []
        self.sequence_pointer: Optional[Node] = None

    def __repr__(self):
        hex_cut = -5  # take last 5 chars of hex representation
        next_addr = hex(id(self.sequence_pointer))[hex_cut:] if self.sequence_pointer else None

        return "{} at {}, {} keys, {} pointers, {} payload, next->{}".format(
            self.node_type, hex(id(self))[hex_cut:], len(self.keys), len(self.pointers), len(self.payload), next_addr)


class BPlusTree:
    """construct a tree with empty root node, or with a given root"""

    def __init__(self, order: int, root: Node = None):
        self.order: int = order
        self.root: Node = root if root else Node(node_type=NodeType.ROOT)
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

    def insert(self, key: int):
        node = self.root
        if node.node_type == NodeType.ROOT and node.pointers == []:
            print("single root in tree")

        while node is not NodeType.LEAF:
            pass

    def range_search(self, left, right):
        """return matching elements within closed interval [left, right]
        1. find position for left
        2. direct elements within interval to the output
        3. search terminates when element larger than right is encountered
        """

        pass

    def search(self, key: int):
        """search for exact position of key, return the
        in actual application, return
        """
        pass

    def fill_type(self, node: Node) -> None:
        if node == self.root:
            node.node_type = NodeType.ROOT
        else:
            if not node.pointers:
                node.node_type = NodeType.LEAF
            else:
                node.node_type = NodeType.NON_LEAF

        for child in node.pointers:
            self.fill_type(child)

    def fill_payload(self, node: Node) -> None:
        if node.node_type is NodeType.LEAF:
            node.payload = [str(key) for key in node.keys]
        else:
            for child in node.pointers:
                self.fill_payload(child)

    def add_sequence_pointers(self) -> None:
        """add sequence pointers between child leaf nodes in place, do for the whole tree"""
        stack = [self.root]
        prev: Optional[Node] = None
        while stack:
            curr = stack.pop()
            if curr.node_type is NodeType.LEAF:
                if prev:
                    prev.sequence_pointer = curr
                    prev = curr
                else:
                    prev = curr
            else:
                for child in reversed(curr.pointers):
                    stack.append(child)

    def traversal(self, node: Node):
        if node.node_type is NodeType.LEAF:
            print(node.payload)
        else:
            for child in node.pointers:
                self.traversal(child)

    def traversal_iterative(self):
        stack = [self.root]
        while stack:
            curr = stack.pop()
            if curr.node_type is NodeType.LEAF:
                print(curr.payload)
            else:
                for child in reversed(curr.pointers):
                    stack.append(child)


# this is a static method.  moving the function to other files may easily cause circular import problems.
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
