# Created by Luming on 11/10/2020 1:47 PM
from math import ceil
from typing import Optional, List, Dict

from BPlusTreeNode import Node, NodeType, get_constraint


class BPlusTree:
    """construct a tree with empty root node, or with a given root"""

    def __init__(self, order: int, root: Node = None, keys: List[int] = None, option='dense'):
        self.option = option
        self.order: int = order
        self.root: Node = root if root else Node(type=NodeType.ROOT)
        self.constraint: Dict = get_constraint(self.order)
        if keys:
            if self.option == 'dense':
                self.root = self.dense_construct(keys)
            elif self.option == 'sparse':
                self.root = self.sparse_construct(keys)

    def get_node_dist_sparse(self, num_nodes: int, node_type: NodeType = NodeType.LEAF) -> List[int]:
        """distribute by sparse"""
        remain = num_nodes
        min_keys = self.constraint[node_type]['min_keys']
        max_keys = self.constraint[node_type]['max_keys']
        ret = []

        while remain > 0:
            if remain <= min_keys:  # extreme case, for root only
                ret.append(remain)
                remain = 0
            elif min_keys < remain <= max_keys:
                ret.append(remain)
                remain = 0
            else:
                ret.append(min_keys)
                remain -= min_keys
        else:
            return ret

    def get_node_dist_dense(self, num_keys: int, node_type: NodeType = NodeType.LEAF) -> List[int]:
        """ apply for dense construct
        if the remaining keys can be divided by min_keys and max_keys, then
        example: order of 3, min=2, max=3, if the remaining=4, divide by one having minimal, and the other having the rest
        otherwise, get a full mount out of the remaining

        there are four cases: dense leaf, dense internal, sparse leaf, sparse internal
        """

        min_keys = self.constraint[node_type]['min_keys']
        max_keys = self.constraint[node_type]['max_keys']

        remain = num_keys
        ret = []
        while remain > 0:
            if remain <= max_keys:
                ret.append(remain)
                remain = 0
            elif max_keys < remain < min_keys + max_keys:
                last = min_keys
                last_but_one = remain - min_keys
                ret.extend([last_but_one, last])
                remain = 0
            else:
                ret.append(max_keys)
                remain -= max_keys
        else:
            # print(ret)
            return ret

    def sparse_construct(self, values: List[int]) -> Node:
        # n = len(values)
        # values.sort()
        # num_nodes =

        pass

    def dense_construct_parents(self, nodes: List[Node]) -> Node:
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
            return self.dense_construct_parents(parent_nodes)

    def dense_construct(self, keys: List[int]) -> Node:
        n = len(keys)
        keys.sort()
        leaf_distribution = self.get_node_dist_dense(len(keys), NodeType.LEAF)
        num_nodes = len(leaf_distribution)
        leaves = []
        start = 0
        for count in leaf_distribution:
            end = start + count
            new_node = Node(keys=keys[start:end], payload=[str(value) for value in keys[start:end]], type=NodeType.LEAF)
            leaves.append(new_node)
            start = end

        # leaves = [Node(keys=values[self.order * i:self.order * (i + 1)],
        #                payload=[str(value) for value in values[self.order * i:self.order * (i + 1)]],
        #                type=NodeType.LEAF)
        #           for i in range(num_nodes)]

        for i in range(len(leaves) - 1):
            leaves[i].sequence_pointer = leaves[i + 1]

        if num_nodes == 1:
            return leaves[0]  # root
        else:
            return self.dense_construct_parents(leaves)

    def is_valid(self, node: Node = None) -> bool:
        """perform constraint check for the given node and all its child node
        handle leaf and non-leaf nodes differently.  check payload for leaf, and pointers for non-leaf.
        """
        if not node:
            node = self.root

        if node.type is NodeType.NONE:  # cannot check node constraint without type
            print("node type not specified")
            return True

        if node.order is None:
            print('node order not set.')
            return False

        if node.type == NodeType.ROOT:
            # check for sequence pointers consistency
            child_nodes = self.get_child_nodes()

            curr = self.get_first_child()
            seq_child_nodes = []
            while curr:
                seq_child_nodes.append(curr)
                curr = curr.sequence_pointer
            else:
                if child_nodes != seq_child_nodes:
                    print("sequence pointer inconsistent.")
                    return False

        if not node.is_valid():
            return False

        for child in node.pointers:
            if not self.is_valid(child):
                return False

        # parent key should be larger than left child max key, and no larger than right child min key
        for i in range(node.get_key_size()):
            if not min(node.pointers[i].keys) < node.keys[i] <= max(node.pointers[i + 1].keys):
                return False

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

    def fill_payload(self, node: Node = None) -> None:
        if node is None:
            node = self.root

        if node.type is NodeType.LEAF:
            node.set_payload()
        else:
            for child in node.pointers:
                self.fill_payload(child)

    def fill_order(self) -> None:
        stack = [self.root]
        while stack:
            curr = stack.pop()
            curr.order = self.order
            stack.extend(curr.pointers[::-1])
            # for child in reversed(curr.pointers):
            #     stack.append(child)

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

    def get_child_nodes(self) -> List[Node]:
        stack = [self.root]
        child_nodes = []
        while stack:
            curr = stack.pop()
            if curr.type == NodeType.LEAF:
                child_nodes.append(curr)
            else:
                for child in reversed(curr.pointers):
                    stack.append(child)
        else:
            return child_nodes

    def get_first_child(self) -> Node:
        curr = self.root
        while True:
            if curr.get_pointer_size() == 0:
                return curr
            else:
                curr = curr.pointers[0]

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
