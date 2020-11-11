# Created by Luming on 11/11/2020 1:26 AM
from bplustree import Node, NodeType, BPlusTree


def get_b_plus_tree(key) -> BPlusTree:
    trees = {
        'l2': BPlusTree(3,
                        Node([17, 29], [
                            Node([5, 7]), Node([17, 19]), Node([29, 31])
                        ])),
        'l3': BPlusTree(3,
                        Node([3], [
                            Node([2], [
                                Node([1]), Node([2]),
                            ]),
                            Node([4], [
                                Node([3]), Node([4, 5])
                            ])
                        ]))
    }
    return trees.get(key, None)


tree = get_b_plus_tree('l3')
root = tree.root
tree.fill_type(root)
tree.fill_payload(root)
tree.add_sequence_pointers()
tree.search(3)
ret = tree.range_search(9, 19)
