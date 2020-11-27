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
    def __init__(self, keys=None, pointers=None, payload: List[Any] = None, type=NodeType.NONE):
        """sequence pointer only works when node type is LEAF
        a node represents a square with multiple values and pointers.

        pointers: in leaf node the list is always empty; in
                  in non-leaf node the list points to child nodes

        Leaf node: key,
        """
        self.type: NodeType = type
        self.keys: List[int] = keys if keys else []
        self.pointers: List[Node] = pointers if pointers else []
        self.payload: List[Any] = payload if payload else []
        self.sequence_pointer: Optional[Node] = None

    def __repr__(self):
        hex_cut = -5  # take last 5 chars of hex representation
        next_addr = hex(id(self.sequence_pointer))[hex_cut:] if self.sequence_pointer else None

        return "{} at {}, {} keys, {} pointers, {} payload, next->{}".format(
            self.type, hex(id(self))[hex_cut:], len(self.keys), len(self.pointers), len(self.payload), next_addr)


class BPlusTree:
    """construct a tree with empty root node, or with a given root"""

    def __init__(self, order: int, root: Node = None, values: List[int] = None):
        self.order: int = order
        self.root: Node = root if root else Node(type=NodeType.ROOT)
        if values:
            self.root = self.construct_from_values(values)

        self.constraint: Dict = gen_constraint(self.order)

    def sparse_construct(self, nodes: List[Node]) -> Node:
        pass

    def dense_construct(self, nodes: List[Node]) -> Node:
        """ 1. extract key values from the given list
            2. split to nodes if num of keys exceed the order
        """
        # with num_nodes, it requires num_nodes-1 parent keys
        parent_keys = [node.keys[0] for node in nodes[1:]]
        num_nodes = ceil(len(parent_keys) / self.order)  # split
        parent_nodes = [Node(keys=parent_keys[self.order * i:self.order * (i + 1)],
                             pointers=nodes[(self.order + 1) * i:(self.order + 1) * (i + 1)],
                             type=NodeType.NON_LEAF)
                        for i in range(num_nodes)]
        if len(parent_nodes) == 1:
            root = parent_nodes[0]
            root.type = NodeType.ROOT
            return root
        else:
            return self.dense_construct(parent_nodes)

    def construct_from_values(self, values: List[int], option='dense') -> Node:
        n = len(values)
        values.sort()
        num_nodes = ceil(n / self.order)
        leaves = [Node(keys=values[self.order * i:self.order * (i + 1)],
                       payload=[str(value) for value in values[self.order * i:self.order * (i + 1)]],
                       type=NodeType.LEAF)
                  for i in range(num_nodes)]

        for i in range(len(leaves) - 1):
            leaves[i].sequence_pointer = leaves[i + 1]

        if num_nodes == 1:
            return leaves[0]  # root
        else:
            if option == 'dense':
                return self.dense_construct(leaves)
            elif option == 'sparse':
                return self.sparse_construct(leaves)

    def met_constraint(self, node: Node) -> bool:
        """perform constraint check for the given node and all its child nodes """
        if node.type is NodeType.NONE:  # cannot check node constraint without type
            print("node type not specified")
            return True

        constr = self.constraint[node.type]
        if constr['min_keys'] <= len(node.keys) <= constr['max_keys'] and \
                constr['min_pointers'] <= len(node.pointers) <= constr['max_pointers']:
            pass
        else:
            print("expect: [{}, {}] keys, [{}, {}] pointers; actual: {}"
                  .format(constr['min_keys'], constr['max_keys'],
                          constr['min_pointers'], constr['max_pointers'], str(node)))
            return False

        # if len(node.keys) < constr['min_keys'] or len(node.keys) > constr['max_keys'] \
        #         or len(node.pointers) < constr['min_pointers'] or len(node.pointers) > constr['max_pointers']:
        #
        #     return False

        for child in node.pointers:
            if not self.met_constraint(child):
                return False
        else:
            return True

    def insert(self, key: int):
        node = self.root
        if node.type == NodeType.ROOT and node.pointers == []:
            print("single root in tree")

        while node is not NodeType.LEAF:
            pass

    def range_search(self, left, right, node: Node = None) -> List[str]:
        """return matching elements within closed interval [left, right]
        1. find position for left
        2. direct elements within interval to the output
        3. search terminates when element larger than right is encountered
        ref: note17, p17
        note that search procedure returns nothing if the target is not found.
        However, in range search, one expects to find the smallest element that's larger than the left bound,
        then continue searching till the right bound.
        if the node is not provided, it defaults to search under the root.
        """
        ret = []
        if not node:
            node = self.root

        leaf = self.search_node(left, node)
        while leaf:
            for idx, key in enumerate(leaf.keys):
                if key < left:
                    continue
                elif left <= key <= right:
                    ret.append(leaf.payload[idx])
                else:
                    return ret
            else:
                leaf = leaf.sequence_pointer
        else:
            return ret

    def search_node(self, target: int, node: Node = None) -> Optional[Node]:
        """given target key value, return the leaf node that possibly contains the value,
        Such leaf node either contains the value, or should contain if empty space remains within.
        When entering a leaf node, if a key value smaller than the target is found,
        then it confirms that such node can hold the target value,
        assuming that it does not violate the parent constraint.
        """
        if not node:  # default to search under the root
            node = self.root

        if node.type is NodeType.LEAF:
            # assume that parent constraint is met, no check is required in leaf level.
            return node
            # for idx, key in enumerate(node.keys):
            #     if key <= target:
            #         return node
            # else:
            #     print("target {} not found.".format(target))
            #     return None
        else:
            search_range = [-float('inf')] + node.keys + [float('inf')]  # add a dummy infinity number for comparison
            for idx in range(len(search_range) - 1):
                if search_range[idx] <= target < search_range[idx + 1]:
                    return self.search_node(target, node.pointers[idx])

    def search(self, target: int, node: Node = None):
        """search for exact position of key within the given node, return the
        in actual application, return
        ref: note17, p4
        """
        if not node:
            node = self.root

        if node.type is NodeType.LEAF:
            for idx, key in enumerate(node.keys):
                if key == target:
                    return node.payload[idx]
            else:
                print("target {} not found.".format(target))
                return None
        else:
            search_range = [-float('inf')] + node.keys + [float('inf')]  # add a dummy infinity number for comparison
            for idx in range(len(search_range) - 1):
                if search_range[idx] <= target < search_range[idx + 1]:
                    return self.search(target, node.pointers[idx])

    def fill_type(self, node: Node) -> None:
        if node == self.root:
            node.type = NodeType.ROOT
        else:
            if not node.pointers:
                node.type = NodeType.LEAF
            else:
                node.type = NodeType.NON_LEAF

        for child in node.pointers:
            self.fill_type(child)

    def fill_payload(self, node: Node) -> None:
        if node.type is NodeType.LEAF:
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
            if curr.type is NodeType.LEAF:
                if prev:
                    prev.sequence_pointer = curr
                    prev = curr
                else:
                    prev = curr
            else:
                for child in reversed(curr.pointers):
                    stack.append(child)

    def traversal(self, node: Node = None):
        """traverse down from the given node to the leaf nodes, print out leaf payload"""
        if not node:
            node = self.root
        if node.type is NodeType.LEAF:
            print(node.payload)
        else:
            for child in node.pointers:
                self.traversal(child)

    def traversal_iterative(self):
        stack = [self.root]
        while stack:
            curr = stack.pop()
            if curr.type is NodeType.LEAF:
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