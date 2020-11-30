# Created by Luming on 11/10/2020 1:47 PM
from __future__ import annotations

from typing import Optional, List, Dict, Any

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

    def __repr__(self):
        return 'order: {}, option: {}, {} keys, {} height'.format(self.order, self.option, self.get_num_keys(),
                                                                  self.get_height())

    def get_constraint(self) -> List[str]:
        return self.root.get_constraint()

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
            keys = [child.get_first_leaf().keys[0] for child in pointers[1:]]
            new_node = Node(keys=keys, pointers=pointers, type=NodeType.NON_LEAF, order=self.order)
            parent_nodes.append(new_node)
            start = end

        if len(parent_nodes) == 1:
            root = parent_nodes[0]
            root.type = NodeType.ROOT
            return root
        else:
            return self.construct_parents(parent_nodes, option)

    def is_valid(self) -> bool:
        """perform constraint check for the given node and all its child node
        handle leaf and non-leaf nodes differently.  check payload for leaf, and pointers for non-leaf.
        """
        node = self.root
        if node.is_leaf() and node.is_root():
            if node.get_key_size() == 0 and node.get_payload_size() == 0 and node.get_pointer_size() == 0:
                # exception: allow empty root node
                print('empty root node')
                return True

        if node.order is None:
            print('node order not set.')
            return False

        if node.is_root():  # test search only in root node
            if not self.test_search('any'):
                return False

        if node.is_root() and not node.is_leaf():
            # exclude the single root leaf case, check sequence pointer only when there are multiple levels.
            # check for sequence pointers consistency
            if self.get_leaf_keys('sequential') != self.get_leaf_keys('topdown'):
                print('leaf key inconsistent: top down != sequential')
                return False

            leaf_nodes = self.get_leaf_nodes()
            curr = self.get_first_leaf()
            seq_child_nodes = []
            while curr:  # compare sequential vs. top down result
                seq_child_nodes.append(curr)
                curr = curr.sequence_pointer
            else:
                if leaf_nodes != seq_child_nodes:
                    print("sequence pointer inconsistent.")
                    return False

        if not node.is_valid():
            return False

        return True

    def insert(self, key: int):
        """1. find possible position within a leaf node that may store this key
        2. insert into the position
        3. on the upper level, check if it overflows
        """
        self.root.insert_key(key, str(key), 0)
        if self.root.is_overflow():
            new_node = self.root.split()
            root_key = new_node.get_first_leaf().keys[0]
            new_root = Node(keys=[root_key], pointers=[self.root, new_node], type=NodeType.ROOT, order=self.order)
            self.root = new_root

    def delete(self, key: int) -> None:
        if self.search(key) is None:
            print('key {} does not exist.'.format(key))
        else:
            self.root.delete_key(key)
            if self.root.is_singular():
                self.root = self.root.pointers[0]
                self.root.type = NodeType.ROOT
            if not self.is_valid():
                raise Exception('deleting key {} results in error'.format(key))

    def range_search(self, left, right) -> List[str]:
        return self.root.range_search(left, right)

    def search_node(self, target: int) -> Optional[Node]:
        return self.search_node(target)

    def search(self, target: int) -> Optional[Any, None]:
        return self.root.search(target)

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
            if curr.is_leaf() and not curr.is_root():  # here exclude the single root case by checking type
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

    def get_num_leaves(self) -> int:
        return self.root.get_num_leaves()

    def get_num_keys(self) -> int:
        """get the number of keys in leaf nodes"""
        return self.root.get_num_keys_total()

    def get_leaf_nodes(self) -> List[Node]:
        return self.root.get_leaf_nodes()

    def get_first_leaf(self) -> Node:
        """get the first leaf under the given node"""
        return self.root.get_first_leaf()

    def get_last_leaf(self) -> Node:
        return self.root.get_last_leaf()

    def get_min_key(self) -> int:
        return self.root.get_min_key()

    def get_max_key(self) -> int:
        return self.root.get_max_key()

    def get_leaf_keys(self, option='sequential') -> List[int]:
        return self.root.get_leaf_keys(option)

    def get_height(self) -> int:
        return self.root.get_height()

    def get_key_layer(self, height: int = 0) -> List[List[int]]:
        """for default argument, return the leaf keys.  For leaves, it traverses top down,
        rather than using sequence pointers"""
        return self.root.get_key_layer(height)

    def print_layers(self):
        for i in reversed(range(self.get_height() + 1)):
            print('H{}: {}'.format(i, self.get_key_layer(i)))
            print()

    def traversal(self, node: Node = None):
        """traverse down from the given node to the leaf nodes, print out leaf payload"""
        return self.root.traversal()

    def traversal_iterative(self):
        return self.root.traversal_iterative()

    def test_search(self, option='any') -> bool:
        """For test only.  Large tree may be slow to verify.  Test if all leaf values can be found by search function.
        this verifies that the tree is built correctly.
        """
        curr = self.get_first_leaf()
        count = 0
        ret = True
        cases = []
        while curr:
            for key in curr.keys:
                count += 1
                if self.search(key) is None:
                    report = 'key {} exist but not found.'.format(key)
                    if option == 'any':
                        print(report)
                        return False
                    else:  # report all not found cases
                        ret = False
                        cases.append(report)
            else:
                curr = curr.sequence_pointer
        else:
            if ret:
                # print('tested {} keys'.format(count))
                return True
            else:
                return False
