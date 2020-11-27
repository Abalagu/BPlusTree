# Created by Luming on 11/27/2020 12:09 PM
from enum import Enum
from math import ceil, floor
from typing import List, Any, Optional


class NodeType(Enum):
    NON_LEAF = 'non_leaf',
    LEAF = 'leaf',
    ROOT = 'root',
    NONE = None,


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

        return "{} at {}, {} keys, {} pointers, {} payload, next->{}".format(
            self.type, self.get_id(), len(self.keys), len(self.pointers), len(self.payload), next_addr)

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
            constraint = get_constraint(self.order)[self.type]

            if not constraint['min_keys'] <= self.get_key_size() <= constraint['max_keys']:
                print("keys expect:actual {}-{}:{}".format(constraint['min_keys'], constraint['max_keys'],
                                                           self.get_key_size()))
                return False

            if self.type == NodeType.LEAF:
                if self.get_payload_size() != self.get_key_size():
                    print(
                        "LEAF: payload expect:actual = {}:{}".format(self.get_key_size(), self.get_payload_size()))
                    return False
            else:
                if not constraint['min_pointers'] <= self.get_pointer_size() <= constraint['max_pointers']:
                    print("pointers expect:actual = {}-{}:{}".format(constraint['min_pointers'],
                                                                     constraint['max_pointers'],
                                                                     self.get_pointer_size()))
                    return False

        # consistency check
        if not self.is_sorted():
            print('keys not sorted.')
            return False

        if self.type == NodeType.LEAF:
            if self.get_key_size() != self.get_payload_size():
                return False
        else:
            if self.get_key_size() + 1 != self.get_pointer_size():
                return False

        return True

    def is_full(self) -> bool:
        """useful when inserting a key.  If a node is full, then insertion will results in node split."""
        constraint = get_constraint(self.order)[self.type]
        if self.get_key_size() == constraint['max_keys']:
            return True
        else:
            return False

    def is_half_full(self) -> bool:
        """useful when deleting a key.  If a node is half full, then deletion will results in node split."""
        constraint = get_constraint(self.order)[self.type]
        if self.get_key_size() == constraint['min_keys']:
            return True
        else:
            return False

    def is_overflow(self) -> bool:
        constraint = get_constraint(self.order)[self.type]
        if self.get_key_size() > constraint['max_keys']:
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
        if self.type == NodeType.LEAF:
            self.payload = [str(key) for key in self.keys]
        else:
            print("setting payload on non-leaf node!")

    def get_height(self) -> int:
        """path down to a leaf node"""
        if self.get_pointer_size() == 0:
            return 0
        else:
            return 1 + self.pointers[0].get_height()


# this is a static method.  moving the function to other files may easily cause circular import problems.
def get_constraint(order: int):
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
