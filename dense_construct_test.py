# Created by Luming on 11/11/2020 6:16 AM
from bplustree import BPlusTree

values = list(range(20))
order = 3
tree = BPlusTree(order, values=values)
root = tree.root
