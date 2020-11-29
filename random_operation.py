# Created by Luming on 11/28/2020 10:22 PM
from numpy import random
from BPlusTree import BPlusTree

keys = random.choice(range(1000), 100, replace=False).tolist()
tree = BPlusTree(3, keys=keys)
if tree.build():
    if tree.test_search():
        print('success')
