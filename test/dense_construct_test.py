# Created by Luming on 11/11/2020 6:16 AM
from typing import List
import numpy as np
from BPlusTree import BPlusTree


def gen_trivial_tree(order: int, num_nodes: int, option: str = 'dense') -> BPlusTree:
    # keys = list(range(1, 2 * num_nodes, 2))
    keys = list(range(1, 1 + num_nodes))
    tree = BPlusTree(order, keys=keys, option=option)
    if tree.build():
        tree.test_search()
        return tree
    else:
        print('build failed')


def gen_trivial_trees(order: int, max_nodes: int, option: str = 'dense') -> List[BPlusTree]:
    trees = []
    for num_nodes in range(1, 1 + max_nodes):
        print("order: {}, num_nodes: {}, option: {}".format(order, num_nodes, option))
        tree = gen_trivial_tree(order, num_nodes, option)

        if tree.is_valid():
            tree.traversal()
        else:
            print("invalid tree.")
        trees.append(tree)
    else:
        return trees


def gen_tree_iterative(order: int, num_nodes: int) -> BPlusTree:
    # keys = list(range(1, 2 * num_nodes, 2))
    keys = list(range(1, 1 + num_nodes))
    tree = BPlusTree(order, keys=[keys[0]])
    for key in keys[1:]:
        tree.insert(key)
    else:
        return tree


def delete_random_iterative(tree: BPlusTree):
    keys = tree.get_leaf_keys()
    np.random.shuffle(keys)
    for key in reversed(keys):
        print('deleting key {}...'.format(key))
        tree.delete(key)
    else:
        print('tree destructed.')


if __name__ == '__main__':
    tree = gen_trivial_tree(3, 200, 'dense')
    # tree.is_valid()
    delete_random_iterative(tree)
    pass
    # tree = gen_tree_iterative(3, 100)
    # tree.is_valid()
    # tree = gen_trivial_tree(3, 100)
    # tree.is_valid()
