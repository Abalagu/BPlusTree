# Created by Luming on 11/26/2020 8:15 PM
from typing import List

import numpy as np

from BPlusTree import BPlusTree


def gen_new_key(tree: BPlusTree) -> int:
    """return a key that does not exist in the current tree"""
    count = 20
    min_key, max_key = tree.get_min_key(), tree.get_max_key()
    while count > 0:
        new_key = np.random.choice(range(min_key - 10, max_key + 10), 1)
        if tree.search(new_key) is None:
            return new_key
        else:
            count -= 1  # handle the case where values in random range are all in the current tree
    else:
        raise Exception('all values in range may exist in the tree')


def random_insert(tree: BPlusTree) -> None:
    new_key = gen_new_key(tree)
    tree.insert(new_key)


def random_operation(tree: BPlusTree, option: str = 'all'):
    """by default, perform an insert """
    random_insert(tree)


def gen_record(key_range, num_record) -> List[int]:
    samples = np.random.choice(key_range, num_record, False).tolist()
    return samples


def experiment():
    key_range = range(100000, 200000)
    num_record = 10000
    keys = gen_record(key_range, num_record)
    trees = []
    for order in [13, 24]:
        for option in ['dense', 'sparse']:
            tree = BPlusTree(order, keys=keys, option=option)
            tree.build()
            trees.append(tree)
            # random_insert(tree)
            tree.test_search()


if __name__ == '__main__':
    # experiment()
    key_range = range(100000, 200000)
    num_record = 10000
    keys = gen_record(key_range, num_record)
    tree = BPlusTree(13, keys=keys, option='dense')
    tree.build()
    tree.insert(100)
    tree.is_valid()
    tree.test_search('any')
