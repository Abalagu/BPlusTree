# Created by Luming on 11/10/2020 1:47 PM
from __future__ import annotations

from typing import Optional, List, Dict

from BPlusTreeNode import Node, NodeType, gen_constraint


class BPlusTree:
    """construct a tree with empty root node, or with a given root"""

    def __init__(self, order: int, root: Node = None, keys: List[int] = None, option='dense'):
        self.option = option
        self.order: int = order
        self.root: Node = root if root else Node(type=NodeType.ROOT)
        self.constraint: Dict = gen_constraint(self.order)
        if keys:
            self.root = self.construct(keys, option)

    def get_constraint(self) -> List[str]:
        ret = ['order {}'.format(self.order)]
        for node_type in NodeType:
            c = self.constraint[node_type]
            info = '{}, pointers [{}-{}], keys [{}-{}]' \
                .format(node_type, c['min_pointers'], c['max_pointers'], c['min_keys'], c['max_keys'])
            ret.append(info)
        else:
            return ret

    def get_node_dist_sparse(self, num_nodes: int, node_type: NodeType = NodeType.LEAF) -> List[int]:
        """distribute by sparse"""
        remain = num_nodes
        if node_type == NodeType.LEAF:
            lower = self.constraint[node_type]['min_keys']
        else:
            lower = self.constraint[node_type]['min_pointers']

        ret = []
        while remain > 0:
            if remain <= lower:  # extreme case, for root only
                ret.append(remain)
                remain = 0
            # when remain - lower < lower, assigning lower to the current mode will make the remaining node
            # violate the constraint, therefore it needs to assign all to the current node.
            elif lower < remain < 2 * lower:
                ret.append(remain)
                remain = 0
            else:
                ret.append(lower)
                remain -= lower
        else:
            return ret

    def get_node_dist(self, num_keys: int, node_type: NodeType = NodeType.LEAF, option: str = 'dense') -> List[int]:
        if option == 'dense':
            leaf_distribution = self.get_node_dist_dense(num_keys, node_type)
        elif option == 'sparse':
            leaf_distribution = self.get_node_dist_sparse(num_keys, node_type)
        else:
            raise Exception('unknown option {}'.format(option))
        return leaf_distribution

    def get_node_dist_dense(self, num_keys: int, node_type: NodeType = NodeType.LEAF) -> List[int]:
        """ apply for dense construct
        if the remaining keys can be divided by min_keys and max_keys, then
        example: order of 3, min=2, max=3, if the remaining=4, divide by one having minimal,
        and the other having the rest.  otherwise, get a full mount out of the remaining

        there are four cases: dense leaf, dense internal, sparse leaf, sparse internal

        for non-leaf nodes, given n child nodes, there are in total n pointers.
        n_0, n_1, ..., n_i, ..., n_M nodes.  sum(n_i for all i) = n

        n_i-1 = number of keys.

        distribute these n pointers to make each

        for leaf node, group based on min_keys;
        for non-leaf node, group based on min_pointers.
        """
        if node_type == NodeType.LEAF:
            lower = self.constraint[node_type]['min_keys']
            upper = self.constraint[node_type]['max_keys']
        else:
            lower = self.constraint[node_type]['min_pointers']
            upper = self.constraint[node_type]['max_pointers']

        remain = num_keys
        ret = []
        while remain > 0:
            if remain <= upper:
                ret.append(remain)
                remain = 0
            elif upper < remain < lower + upper:
                last = lower
                last_but_one = remain - lower
                ret.extend([last_but_one, last])
                remain = 0
            else:
                ret.append(upper)
                remain -= upper
        else:
            return ret

    def construct(self, keys: List[int], option: str = 'dense') -> Node:
        """build dense b+ tree from a provided list of keys.
        1. build leaf nodes. add sequence pointer
        2. build parent nodes recursively, until a single node is returned as the root.
        """
        keys.sort()
        leaf_distribution = self.get_node_dist(len(keys), NodeType.LEAF, option)
        leaves = []
        start = 0
        for count in leaf_distribution:
            end = start + count
            new_node = Node(keys=keys[start:end],
                            payload=[str(key) for key in keys[start:end]],
                            type=NodeType.LEAF,
                            order=self.order)
            leaves.append(new_node)
            start = end

        for i in range(len(leaves) - 1):
            leaves[i].sequence_pointer = leaves[i + 1]

        num_nodes = len(leaf_distribution)
        if num_nodes == 1:
            return leaves[0]
        else:
            return self.construct_parents(leaves, option)

    def construct_parents(self, nodes: List[Node], option: str = 'dense') -> Node:
        """ 1. extract key values from the given list
            2. split to nodes if num of keys exceed the order
        """
        # with num_nodes, it requires num_nodes-1 parent keys
        curr_height = nodes[0].get_height() + 1
        pointer_distribution = self.get_node_dist(len(nodes), NodeType.NON_LEAF, option)
        parent_nodes = []
        start = 0
        for count in pointer_distribution:
            end = start + count
            pointers = nodes[start:end]
            if curr_height < 2:
                keys = [child.keys[0] for child in pointers[1:]]
            else:  # see discussion on internal node key source with height >= 2
                keys = [child.pointers[0].keys[0] for child in pointers[1:]]
            new_node = Node(keys=keys, pointers=pointers, type=NodeType.NON_LEAF, order=self.order)
            parent_nodes.append(new_node)
            start = end

        if len(parent_nodes) == 1:
            root = parent_nodes[0]
            root.type = NodeType.ROOT
            return root
        else:
            return self.construct_parents(parent_nodes, option)

    def is_valid(self, node: Node = None) -> bool:
        """perform constraint check for the given node and all its child node
        handle leaf and non-leaf nodes differently.  check payload for leaf, and pointers for non-leaf.
        """
        if not node:
            node = self.root

        if node.order is None:
            print('node order not set.')
            return False

        if node.type == NodeType.ROOT and node.get_height() > 0:
            # exclude the single root leaf case, check sequence pointer only when there are multiple levels.
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
        if not node.is_leaf():  # to include single root leaf case, check if the node has child pointers.
            for i in range(node.get_key_size()):
                if not min(node.pointers[i].keys) < node.keys[i] <= max(node.pointers[i + 1].keys):
                    print('violate b+tree < x <= rule')
                    return False

        return True

    def insert(self, key: int):
        """1. find possible position within a leaf node that may store this key
        2. insert into the position
        3. on the upper level, check if it overflows
        """
        node = self.root
        node.insert_key(key)

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

        if node.is_leaf():
            # assume that parent constraint is met, no check is required in leaf level.
            return node
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

        leaf = self.search_node(target, node)
        for idx, key in enumerate(leaf.keys):
            if key == target:
                return leaf.payload[idx]
        else:
            print("target {} not found.".format(target))
            return None

    def fill_type(self, node: Node = None) -> None:
        if node is None:
            node = self.root

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

        if node.is_leaf():
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
            if curr.type is NodeType.LEAF:  # here exclude the single root case by checking type, not using .is_leaf()
                if prev:
                    prev.sequence_pointer = curr
                    prev = curr
                else:
                    prev = curr
            else:
                for child in reversed(curr.pointers):
                    stack.append(child)

    def build(self) -> bool:
        """try to build a tree from given key structure,
        return if the build is successful and if the resulting tree is valid"""
        self.fill_order()
        self.fill_type()
        self.fill_payload()
        self.add_sequence_pointers()
        return self.is_valid()

    def get_child_nodes(self) -> List[Node]:
        stack = [self.root]
        child_nodes = []
        while stack:
            curr = stack.pop()
            if curr.is_leaf():
                child_nodes.append(curr)
            else:
                for child in reversed(curr.pointers):
                    stack.append(child)
        else:
            return child_nodes

    def get_first_child(self) -> Node:
        curr = self.root
        while True:
            if curr.is_leaf():
                return curr
            else:
                curr = curr.pointers[0]

    def get_height(self, node: Node = None) -> int:
        if not node:
            return self.root.get_height()
        else:
            return node.get_height()

    def get_key_layer(self, height: int = 0) -> List[List[int]]:
        """for default argument, return the leaf keys.  For leaves, it traverses top down,
        rather than using sequence pointers"""
        return self.root.get_key_layer(height)

    def traversal(self, node: Node = None):
        """traverse down from the given node to the leaf nodes, print out leaf payload"""
        if not node:
            node = self.root
        if node.is_leaf():
            print(node.payload)
        else:
            for child in node.pointers:
                self.traversal(child)

    def traversal_iterative(self):
        stack = [self.root]
        while stack:
            curr = stack.pop()
            if curr.is_leaf():
                print(curr.payload)
            else:
                for child in reversed(curr.pointers):
                    stack.append(child)

    def test_search(self) -> bool:
        """For test only.  Large tree may be slow to verify.  Test if all leaf values can be found by search function.
        this verifies that the tree is built correctly.
        """
        curr = self.get_first_child()
        count = 0
        while curr:
            for key in curr.keys:
                count += 1
                if self.search(key) is None:
                    print('key {} exist but not found.'.format(key))
                    return False
            else:
                curr = curr.sequence_pointer
        else:
            print('tested {} keys'.format(count))
            return True
