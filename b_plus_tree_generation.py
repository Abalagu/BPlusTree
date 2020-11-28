# Created by Luming on 11/11/2020 1:26 AM
from BPlusTree import Node, NodeType, BPlusTree


def get_tree(key) -> BPlusTree:
    # l2 for two layers, l3 for three layers, small size b plus tree for testing
    trees = {
        'l2': BPlusTree(3,
                        Node([17, 29], [
                            Node([5, 7]), Node([17, 19]), Node([29, 31])
                        ])),
        'l3': BPlusTree(3, keys=list(range(15)))

    }
    return trees.get(key, None)


tree = get_tree('l3')

if tree.build() is not None:
    tree.search(3)
    ret = tree.range_search(9, 19)
    tree.root.get_key_layer(0)
# tree.is_valid()
