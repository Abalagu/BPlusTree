# Created by Luming on 11/27/2020 12:09 PM
from __future__ import annotations

from enum import Enum
from math import ceil, floor
from typing import List, Any, Optional, Union


class NodeType(Enum):
    NON_LEAF = 'non_leaf',
    LEAF = 'leaf',
    ROOT = 'root',


class Node:
    def __init__(self, keys=None, pointers=None, payload: List[Any] = None, type=NodeType.LEAF,
                 order: int = None):
        """sequence pointer only works when node type is LEAF
        a node represents a square with multiple values and pointers.

        pointers: in leaf node the list is always empty; in
                  in non-leaf node the list points to child nodes

        Leaf node: key,
        """
        self.order: int = order
        self.type: NodeType = type
        self.keys: List[int] = keys if keys else []
        self.pointers: List[Node] = pointers if pointers else []
        self.payload: List[Any] = payload if payload else []
        self.sequence_pointer: Optional[Node] = None

    def __repr__(self):

        next_addr = self.sequence_pointer.get_id() if self.sequence_pointer else None

        return "\n{} in memory {}, {} keys, {} pointers, {} payload, at height {}, next->{}\nkeys={}\n\n".format(
            self.type, self.get_id(), len(self.keys), len(self.pointers), len(self.payload), self.get_height(),
            next_addr, self.keys)

    def get_id(self, hex_cut=-5):
        # take last 5 chars of hex representation
        return hex(id(self))[hex_cut:]

    def describe(self) -> str:
        """return the keys and hex id of the node"""
        ret = 'id: {}, keys: {}'.format(self.get_id(), self.keys)
        return ret

    def is_valid(self) -> bool:
        """check if a node conforms with the constraint, check for child and parent consistency goes to b plus tree"""

        # bound check, only valid in context, i.e., when order is provided
        if self.order is not None:
            constraint = gen_constraint(self.order)[self.type]

            if not constraint['min_keys'] <= self.get_key_size() <= constraint['max_keys']:
                print(self)
                print("keys expect:actual {}-{}:{}"
                      .format(constraint['min_keys'], constraint['max_keys'], self.get_key_size()))
                return False

            if self.is_leaf():  # include single root leaf case
                if self.get_payload_size() != self.get_key_size():
                    print("LEAF: payload expect:actual = {}:{}"
                          .format(self.get_key_size(), self.get_payload_size()))
                    return False
            else:
                if not constraint['min_pointers'] <= self.get_pointer_size() <= constraint['max_pointers']:
                    print("pointers expect:actual = {}-{}:{}".format(constraint['min_pointers'],
                                                                     constraint['max_pointers'],
                                                                     self.get_pointer_size()))
                    return False

        # consistency check
        if not self.is_sorted():
            print('keys not sorted. keys: {}, height: {}'.format(self.keys, self.get_height()))
            return False

        if self.is_leaf():
            if self.get_key_size() != self.get_payload_size():
                return False
        else:
            if self.get_key_size() + 1 != self.get_pointer_size():
                return False

        # check that all child are of the same height.
        if not self.is_leaf():
            ref_height = self.pointers[0].get_height()
            if not all([child.get_height() == ref_height for child in self.pointers]):
                print('child height inconsistent')
                print(self)
                return False

        # parent key should be larger than left child max key, and no larger than right child min key
        if not self.is_leaf():  # to include single root leaf case, check if the node has child pointers.
            for i in range(self.get_key_size()):
                if not self.pointers[i].get_max_key() < self.keys[i] <= self.pointers[i + 1].get_min_key():
                    print('key {} violate b+tree < x <= rule'.format(self.keys[i]))
                    return False

        for child in self.pointers:
            if not child.is_valid():
                return False

        return True

    def is_root(self) -> bool:
        return self.type == NodeType.ROOT

    def is_leaf(self) -> bool:
        """a node cannot tell if it is the root within the tree, but it can tell that it is the leaf if it has no child
        replace the use of == NodeType.LEAF if possible.
        """
        return self.get_height() == 0

    def is_singular(self) -> bool:
        """check if the node contains only a single child.  in this case, the child should replace the parent"""
        return self.get_key_size() == 0 and self.get_pointer_size() == 1

    def is_empty(self) -> bool:
        return self.get_key_size() == 0

    def is_full(self) -> bool:
        """useful when inserting a key.  If a node is full, then insertion will results in node split."""
        constraint = gen_constraint(self.order)[self.type]
        if self.get_key_size() == constraint['max_keys']:
            return True
        else:
            return False

    def is_half_full(self) -> bool:
        """useful when deleting a key.  If a node is half full, then deletion will results in node split."""
        constraint = gen_constraint(self.order)[self.type]
        if self.get_key_size() == constraint['min_keys']:
            return True
        else:
            return False

    def is_plenty(self) -> bool:
        """return True if the node contains more than min_keys, which is suitable for redistribution"""
        constraint = gen_constraint(self.order)[self.type]
        if constraint['min_keys'] < self.get_key_size() <= constraint['max_keys']:
            # not sure if the max key limit should be enforced.  trying to redistribute an overflow node?
            return True
        else:
            return False

    def has_left_sibling(self, idx: int) -> bool:
        """return true if the idx-th child has a left sibling.  check sibling condition at parent level.
        precondition for redistribution and merge.
        return True only when it is an internal node, the index is within child range, and it has left sibling.

        reject negative index in this usage, avoid tail indexing.
        """
        if not self.is_leaf() and 0 <= idx < self.get_pointer_size():
            return idx > 0
        else:
            return False

    def has_right_sibling(self, idx: int) -> bool:
        if not self.is_leaf() and 0 <= idx < self.get_pointer_size():
            return idx < self.get_pointer_size() - 1
        else:
            return False

    def is_overflow(self) -> bool:
        constraint = gen_constraint(self.order)[self.type]
        if self.get_key_size() > constraint['max_keys']:
            return True
        else:
            return False

    def is_underflow(self) -> bool:
        constraint = gen_constraint(self.order)[self.type]
        if self.get_key_size() < constraint['min_keys']:
            return True
        else:
            return False

    def is_sorted(self) -> bool:
        return sorted(self.keys) == self.keys

    def get_key_size(self) -> int:
        return len(self.keys)

    def get_pointer_size(self) -> int:
        return len(self.pointers)

    def get_payload_size(self) -> int:
        return len(self.payload)

    def set_payload(self) -> None:
        if self.is_leaf():
            self.payload = [str(key) for key in self.keys]
        else:
            print("setting payload on non-leaf node!")

    def get_height(self) -> int:
        """path down to a leaf node
        height = 0 means it is a leaf node, which accommodates for single root leaf case.
        """
        if self.get_pointer_size() == 0:
            return 0
        else:
            return 1 + self.pointers[0].get_height()

    def get_constraint(self) -> List[str]:
        ret = ['order {}'.format(self.order)]
        constraint = gen_constraint(self.order)
        for node_type in NodeType:
            c = constraint[node_type]
            info = '{}, pointers [{}-{}], keys [{}-{}]' \
                .format(node_type, c['min_pointers'], c['max_pointers'], c['min_keys'], c['max_keys'])
            ret.append(info)
        else:
            return ret

    def get_first_leaf(self) -> Node:
        curr = self
        while True:
            if curr.is_leaf():
                return curr
            else:
                curr = curr.pointers[0]

    def get_last_leaf(self) -> Node:
        curr = self
        while True:
            if curr.is_leaf():
                return curr
            else:
                curr = curr.pointers[-1]

    def get_leaf_keys(self, option='sequential') -> List[int]:
        """return all leaf keys under the current node."""
        if option == 'sequential':
            return self.get_leaf_keys_sequential()
        elif option == 'topdown':
            return self.get_leaf_keys_top_down()
        else:
            raise Exception('unknown option')

    def get_leaf_keys_top_down(self) -> List[int]:
        leaves = self.get_leaf_nodes()
        return [key for leaf in leaves for key in leaf.keys]

    def get_leaf_keys_sequential(self) -> List[int]:
        curr = self.get_first_leaf()
        ret = []
        while curr:
            ret.extend(curr.keys)
            curr = curr.sequence_pointer
        else:
            return ret

    def get_min_key(self) -> int:
        return self.get_first_leaf().keys[0]

    def get_max_key(self) -> int:
        return self.get_last_leaf().keys[-1]

    def get_num_leaves(self) -> int:
        return len(self.get_leaf_nodes())

    def get_num_keys_total(self) -> int:
        """get the number of keys in leaf nodes"""
        leaves = self.get_leaf_nodes()
        return sum([leaf.get_key_size() for leaf in leaves])

    def get_key_idx(self, key: int) -> Optional[int]:
        """search for exact position of a given key.  If not found, return None."""
        if key in self.keys:
            return self.keys.index(key)
        else:
            return None

    def get_index(self, key: int) -> int:
        """for the given key, find the index to insert that maintains the sorted nature of all the keys
        find the index such that self.keys[i-1] <= key <= self.keys[i], so that self.keys.insert(key, i) inserts
        before index i and the list maintains sorted.

        this somehow also works for finding the child node that may store the key value.
        if there are no child pointers, then it is leaf itself, and it returns a possible slot to insert.
        if there are child pointers, then it returns the one
        """
        comparison = [-float('inf')] + self.keys + [float('inf')]
        for i in range(len(comparison) - 1):
            if comparison[i] <= key < comparison[i + 1]:
                return i

    def get_leaf_nodes(self) -> List[Node]:
        """top down approach"""
        stack = [self]
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

    def search_node(self, target: int) -> Optional[Node]:
        """given target key value, return the leaf node that possibly contains the value,
        Such leaf node either contains the value, or should contain if empty space remains within.
        When entering a leaf node, if a key value smaller than the target is found,
        then it confirms that such node can hold the target value,
        assuming that it does not violate the parent constraint.
        """
        if self.is_leaf():
            # assume that parent constraint is met, no check is required in leaf level.
            return self
        else:
            search_range = [-float('inf')] + self.keys + [float('inf')]  # add a dummy infinity number for comparison
            for idx in range(len(search_range) - 1):
                if search_range[idx] <= target < search_range[idx + 1]:
                    return self.pointers[idx].search_node(target)

    def search(self, target: int) -> Optional[Any, None]:
        """search for exact position of key within the given node, return the
        in actual application, return
        ref: note17, p4
        """
        leaf = self.search_node(target)
        for idx, key in enumerate(leaf.keys):
            if key == target:
                return leaf.payload[idx]
        else:
            # print("target {} not found.".format(target))
            return None

    def range_search(self, left, right) -> List[str]:
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
        leaf = self.search_node(left)
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

    def insert_key(self, key: int, data: Union[str, Node], height: int = 0):
        """insert key to a leaf node.  When calling directly to a leaf node, possible overflow will not be handled
        unless its parent node checks.
        it defaults to inserting to a leaf node.  If specified, insert to a child node.
        if inserting to a leaf, data should be string;
        if inserting to a internal node, data should be the new child Node
        """
        if self.get_height() < height:
            raise Exception('cannot reach above. {} < {}'.format(self.get_height(), height))

        if self.get_height() == height:
            print('INSERTING KEY: {}'.format(key))
            print('BEFORE INSERTION: {}'.format(self))
            idx = self.get_index(key)  # find suitable position
            self.keys.insert(idx, key)
            if self.is_leaf():
                self.payload.insert(idx, data)
            else:
                self.pointers.insert(idx, data)
            print('AFTER INSERTION: {}'.format(self))

        else:  # dig down into lower layer, pass data down
            idx = self.get_index(key)
            self.pointers[idx].insert_key(key, data, height)
            if self.pointers[idx].is_overflow():
                print('INSERTION OVERFLOW')
                print('NODE BEFORE SPLIT: {}'.format(self.pointers[idx]))
                new_node = self.pointers[idx].split()
                print('NODE AFTER SPLIT: {}'.format(self.pointers[idx]))
                print('NEW NODE: {}'.format(new_node))
                # insert to the right of the original node that just got split
                print('NODE BEFORE INSERT: {}'.format(self))
                self.pointers.insert(idx + 1, new_node)
                self.keys.insert(idx, self.pointers[idx + 1].get_first_leaf().keys[0])
                print('NODE AFTER INSERT: {}'.format(self))

    def traversal(self):
        """traverse down from the given node to the leaf nodes, print out leaf payload"""
        if self.is_leaf():
            print(self.payload)
        else:
            for child in self.pointers:
                child.traversal()

    def traversal_iterative(self):
        stack = [self]
        while stack:
            curr = stack.pop()
            if curr.is_leaf():
                print(curr.payload)
            else:
                for child in reversed(curr.pointers):
                    stack.append(child)

    def print_layers(self):
        print('TREE ROOTED UNDER: {}'.format(self))
        for i in reversed(range(self.get_height() + 1)):
            print('H{}: {}'.format(i, self.get_key_layer(i)))
            print()

    def merge(self, idx: int) -> bool:
        """at parent perspective, merge node idx+1 into node idx. return True if success else False
        there is no difference between left merge and right merge.  node1, node2, node3.  node1 right merge into node2
        is the same as node2 left merge into node1.  Therefore one implementation is sufficient.

        merge idx+1 into node idx.  For right most leaf with no next node, call merge(idx-1) if it has left sibling.
        """
        node = self.pointers[idx]
        if not self.has_right_sibling(idx) or self.pointers[idx + 1].is_full():
            return False
        else:
            next_node = self.pointers[idx + 1]
            print('FIX BY MERGING')
            print('LEFT NODE BEFORE MERGE: {}'.format(self.pointers[idx]))
            print('RIGHT NODE BEFORE MERGE: {}'.format(next_node))

        if node.is_leaf():
            node.keys.extend(next_node.keys)
            node.payload.extend(next_node.payload)
            self.keys.pop(idx)
            self.pointers.pop(idx + 1)
            node.sequence_pointer = next_node.sequence_pointer
            # when merge results in parent having 0 key 1 pointer, make the merged node as self.
            # however, this can only be handled by self.parent.
        else:
            node.keys.append(next_node.get_min_key())
            node.keys.extend(next_node.keys)
            node.pointers.extend(next_node.pointers)
            self.keys.pop(idx)
            self.pointers.pop(idx + 1)

        print('NODE AFTER MERGE: {}'.format(self.pointers[idx]))
        return True

    def redistribute(self, idx: int) -> bool:
        """redistribute a key from a sibling of the idx-th child to it.  return True if success else False"""
        node = self.pointers[idx]
        if self.has_left_sibling(idx) and self.pointers[idx - 1].is_plenty():
            print('FIX BY BORROW FROM LEFT SIBLING')
            left_sibling = self.pointers[idx - 1]
            print('LEFT SIBLING BEFORE BORROW: {}'.format(left_sibling))
            if node.is_leaf():
                # max key of the left sibling, redistribute to be the min key of the node
                moving_key = left_sibling.keys.pop()
                moving_payload = left_sibling.payload.pop()
                node.keys.insert(0, moving_key)
                node.payload.insert(0, moving_payload)
                self.keys[idx - 1] = moving_key  # min key from the right sub-tree
            else:
                new_key = node.get_min_key()
                moving_child = left_sibling.pointers.pop()
                left_sibling.keys.pop()  # simply remove the right most key
                node.pointers.insert(0, moving_child)
                node.keys.insert(0, new_key)
                self.keys[idx - 1] = node.get_min_key()  # update since node gets a new left most leaf

            print('LEFT SIBLING AFTER BORROW: {}'.format(left_sibling))
            print('UNDERFLOW NODE AFTER BORROW: {}'.format(self.pointers[idx]))
            return True

        elif self.has_right_sibling(idx) and self.pointers[idx + 1].is_plenty():
            right_sibling = self.pointers[idx + 1]
            print('FIX BY BORROW FROM RIGHT')
            print('RIGHT SIBLING BEFORE BORROW: {}'.format(right_sibling))
            if node.is_leaf():
                new_key = right_sibling.keys.pop(0)  # min key of the right sibling
                node.keys.append(new_key)
                moving_payload = right_sibling.payload.pop(0)
                node.payload.append(moving_payload)
                self.keys[idx] = right_sibling.get_min_key()
            else:
                moving_child = right_sibling.pointers.pop(0)
                right_sibling.keys.pop(0)
                node.pointers.append(moving_child)
                node.keys.append(moving_child.get_min_key())
                # right_sibling.keys[0] = right_sibling.pointers[1].get_min_key()
                self.keys[idx] = right_sibling.get_min_key()

            print('RIGHT SIBLING AFTER BORROW: {}'.format(right_sibling))
            print('UNDERFLOW NODE AFTER BORROW: {}'.format(self.pointers[idx]))
            return True

        else:  # redistribution fails, try merge with siblings.
            return False

    def delete_key(self, key: int) -> None:
        if self.is_leaf():
            print('NODE BEFORE DELETE: {}'.format(self))
            idx = self.get_key_idx(key)
            if idx is not None:
                self.keys.pop(idx)
                self.payload.pop(idx)
                print('NODE AFTER DELETE: {}'.format(self))
            else:
                print('key to delete: {} not found.'.format(key))
        else:
            node_idx = self.get_index(key)
            self.pointers[node_idx].delete_key(key)

            # should fix height difference by rotating a higher node key.
            # same as redistribution
            if self.pointers[node_idx].is_underflow():
                print('UNDERFLOW CAUSED BY DELETE')
                print('NODE BEFORE FIX: {}'.format(self.pointers[node_idx]))
                # priority: redistribution > merge
                # try merge with neighbor nodes
                if self.redistribute(node_idx):
                    return
                elif self.merge(node_idx):  # merge curr and right
                    return
                elif self.merge(node_idx - 1):  # merge left and curr
                    return
                else:  # singular case,
                    print('singular case, cannot redistribute nor merge')

    def split(self) -> Node:
        """split an overflow node and return two nodes.  By default the split is left biased,
        that the left node has more keys than the right node.  Return the new node that is to be put to the right of
        the current one, while the original one is the left node.

        The split behavior depends on the height of the node.

        split of root: root -> leaf, root -> non-leaf
        """
        if self.is_overflow():
            if self.is_leaf():
                cut = (self.get_key_size() + 1) // 2
                new_node = Node(keys=self.keys[cut:], payload=[str(key) for key in self.keys[cut:]], type=NodeType.LEAF,
                                order=self.order)
                new_node.sequence_pointer = self.sequence_pointer
                self.sequence_pointer = new_node

                self.keys = self.keys[:cut]
                self.payload = [str(key) for key in self.keys]
                self.type = NodeType.LEAF  # for single root tree split to leaf case
                return new_node
            else:  # when splitting an internal node, the median value upgrades to the upper height
                # should slice child pointers for new node and original node
                # cut = (self.get_key_size() + 1) // 2
                cut = self.get_key_size() // 2
                keys = self.keys
                pointers = self.pointers
                new_node = Node(keys=keys[cut + 1:], pointers=pointers[cut + 1:], type=NodeType.NON_LEAF,
                                order=self.order)
                self.keys = keys[:cut]
                self.pointers = pointers[:cut + 1]
                self.type = NodeType.NON_LEAF  # for root split to internal node case
                return new_node
        else:
            raise Exception('requesting split on a not overflow node')

    def get_key_layer(self, height=None) -> List[List[int]]:
        """return a list of key lists for nodes at the given height, a horizontal section of keys.
        height=0 -> leaf keys
        height=1 -> keys from parents of leaf
        """
        if height is None:
            return [self.keys]

        if height > self.get_height():
            print('given height higher than current node')
            return []

        dig = self.get_height() - height  # dig x steps downward
        nodes: List[Node] = [self]
        while dig > 0:
            nodes = [child for node in nodes for child in node.pointers]
            dig -= 1
        else:
            return [node.keys for node in nodes]


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
