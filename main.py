from bplustree import BPlusTree, Node, NodeType

tree = BPlusTree(3, Node(NodeType.ROOT))
print(tree.constraint)
