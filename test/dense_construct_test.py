# Created by Luming on 11/11/2020 6:16 AM
from BPlusTree import BPlusTree

for num_nodes in range(1, 20):
    keys = list(range(1, 1 + num_nodes))
    order = 5
    option = 'sparse'
    tree = BPlusTree(order, keys=keys, option=option)

    print("order: {}, num_nodes: {}, option: {}".format(order, num_nodes, option))
    if tree.build():
        tree.traversal()
    else:
        print("invalid tree.")
