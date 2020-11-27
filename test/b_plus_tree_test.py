# Created by Luming on 11/10/2020 2:50 PM
from BPlusTree import BPlusTree, Node, NodeType


def tree_init(order: int):
    tree = BPlusTree(order)
    return tree


def constraint_check(tree):
    return tree.met_constraint(tree.root)


#
# order = 3
# tree = tree_init(order)
# constraint_check(tree)


def construct_tree() -> BPlusTree:
    tree_1 = BPlusTree(3, Node([5, 29], ['5', '29'], type=NodeType.ROOT))
    tree_2 = BPlusTree(3, Node([17], [
        Node(NodeType.LEAF, [5, 7], ['5', '7']), Node(NodeType.LEAF, [17, 29], ['17', '29'])
    ], type=NodeType.ROOT))
    tree_2.root.pointers[0].sequence_pointer = tree_2.root.pointers[1]
    return tree_2


tree = construct_tree()
