# Created by Luming on 11/10/2020 2:50 PM
from bplustree import BPlusTree


def tree_init(order: int):
    tree = BPlusTree(order)
    return tree


def constraint_check(tree):
    return tree.met_constraint(tree.root)


order = 3
tree = tree_init(order)
constraint_check(tree)
