# Created by Luming on 11/26/2020 9:27 PM
from typing import List

from BPlusTree import get_constraint, NodeType, BPlusTree

if __name__ == '__main__':
    order = 3
    tree = BPlusTree(order)
    node_type = NodeType.LEAF
    num_nodes = 4
    # get_node_dist_dense(order, num_nodes)
    tree.get_node_dist_sparse(num_nodes, NodeType.NON_LEAF)
    pass
    # for i in range(10):
    #     keys = list(range(i + 1))
    #     tree = BPlusTree(order, keys=keys)
    #     print('order: {}, num_keys:{}'.format(order, len(keys)))
    #     tree.traversal()
