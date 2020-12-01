# Created by Luming on 11/30/2020 11:57 AM
from typing import List

from BPlusTree import BPlusTree

import numpy as np


def gen_record(key_range, num_record) -> List[int]:
    samples = np.random.choice(key_range, num_record, False).tolist()
    return samples


def test_init() -> List[BPlusTree]:
    key_range = range(100000, 200000)
    num_record = 10000
    keys = gen_record(key_range, num_record)
    trees = []
    tree_orders = [13, 24]
    for order in tree_orders:
        for option in ['dense', 'sparse']:
            tree = BPlusTree(order, keys=keys, option=option)
            if tree.build():
                trees.append(tree)
            else:
                raise Exception('tree build error')
    else:
        return trees


def gen_new_key(tree: BPlusTree) -> int:
    """return a key that does not exist in the current tree"""
    # count = 20
    min_key, max_key = tree.get_min_key(), tree.get_max_key()
    while True:
        new_key = np.random.choice(range(min_key - 10, max_key + 10), 1)[0]
        if tree.search(new_key) is None:
            return new_key
        # else:
        #     count -= 1  # handle the case where values in random range are all in the current tree
    # else:
    #     raise Exception('all values in range may exist in the tree')


def random_insert(tree: BPlusTree) -> None:
    new_key = gen_new_key(tree)
    tree.insert(new_key)
    print('insert new key {}'.format(new_key))


def random_delete(tree: BPlusTree) -> None:
    key = np.random.choice(tree.get_leaf_keys(), 1)[0]
    tree.delete(key)
    print('delete key {}'.format(key))


def random_operation(tree: BPlusTree):
    """by default, perform an insert """
    funcs = [random_insert, random_delete]
    func = np.random.choice(funcs)
    func(tree)


def operations(tree: BPlusTree):
    for i in range(2):
        random_insert(tree)
    else:
        if not tree.is_valid():
            raise

    for i in range(2):
        random_delete(tree)
    else:
        if not tree.is_valid():
            raise

    for i in range(5):
        random_operation(tree)
    else:
        if not tree.is_valid():
            raise


# def test_tear_down(tree: BPlusTree):
#     trees = test_init()
#     for tree in trees:
#         delete_random_iterative(tree)
#
#     pass


def experiment():
    trees = test_init()
    for tree in trees:
        print(tree)
        operations(tree)
        # random_operation(tree)
        if not tree.is_valid():
            raise Exception('tree not valid after random op')
    else:
        print('tree pass random operation test')


def gen_trivial_tree(order: int, num_nodes: int, option: str = 'dense') -> BPlusTree:
    keys = list(range(1, 2 * num_nodes, 2))
    # keys = list(range(1, 1 + num_nodes))
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


def batch_test():
    for order in [13, 24]:
        for option in ['dense', 'sparse']:
            tree = gen_trivial_tree(order, 1000, option)
            if not tree.is_valid():
                print('tree not valid')
                return
                # delete_random_iterative(tree)
    else:
        print('pass batch test')


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
    for key in keys:
        # print('deleting key {}...'.format(key))
        tree.delete(key)
        if not tree.is_valid():
            raise Exception('deleting key {} results in error'.format(key))
    else:
        print('{} keys deleted.  tree destructed.'.format(len(keys)))


def is_valid_test():
    tree = gen_trivial_tree(3, 20, 'dense')
    tree.is_valid()


def random_operation_test(order: int, num_nodes: int, option: str, num_trial: int):
    for i in range(num_trial):
        tree = gen_trivial_tree(order, num_nodes, option)
        for j in range(5):
            random_operation(tree)
        else:
            if not tree.is_valid():
                print('fail test')
                return
    else:
        print('pass test')


if __name__ == '__main__':
    experiment()
    # random_operation_test(13, 2000, 'dense', 5)
    # is_valid_test()
    # trees = test_init()
    # for tree in trees:
    #     for i in range(5):
    #         random_delete(tree)
    #         if not tree.is_valid():
    #             raise Exception('tree not valid after deletion')
