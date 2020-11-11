from bplustree import BPlusTree, Node, NodeType

tree = BPlusTree(3, Node(node_type=NodeType.ROOT))
print(tree.constraint)
