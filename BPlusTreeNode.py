# Created by Luming on 11/27/2020 12:09 PM
from __future__ import annotations

from enum import Enum
from math import ceil, floor
from typing import List, Any, Optional, Union


class NodeType(Enum):
    NON_LEAF = 'non_leaf',
    LEAF = 'leaf',
    ROOT = 'root',
    # NONE = None,
    # NON_LEAF = 'non_leaf',
    # LEAF = 'leaf',
    # ROOT = 'root',
    # NONE = None,


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

        return "{} at {}, {} keys, {} pointers, {} payload, next->{}\nkeys={}".format(
            self.type, self.get_id(), len(self.keys), len(self.pointers), len(self.payload), next_addr, self.keys)

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

        return True

    def is_root(self) -> bool:
        return self.type == NodeType.ROOT

    def is_leaf(self) -> bool:
        """a node cannot tell if it is the root within the tree, but it can tell that it is the leaf if it has no child
        replace the use of == NodeType.LEAF if possible.
        """
        return self.get_height() == 0

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
            idx = self.get_index(key)  # find suitable position
            self.keys.insert(idx, key)
            if self.is_leaf():
                self.payload.insert(idx, data)
            else:
                self.pointers.insert(idx, data)
            # if self.is_overflow():
            #     print('child overflow, requires handling by parent')

        else:  # dig down into lower layer, pass data down
            idx = self.get_index(key)
            self.pointers[idx].insert_key(key, data, height)
            if self.pointers[idx].is_overflow():
                new_node = self.pointers[idx].split()
                # insert to the right of the original node that just got split
                self.pointers.insert(idx + 1, new_node)
                # self.keys.insert(idx + 1, self.pointers[idx + 1].get_first_leaf().keys[0])
                self.keys.insert(idx, self.pointers[idx + 1].get_first_leaf().keys[0])

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
                cut = (self.get_key_size() + 1) // 2
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
