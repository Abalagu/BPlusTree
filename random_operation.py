# Created by Luming on 11/28/2020 10:22 PM

from test_functions import *

tree = gen_trivial_tree(2, 20, 'dense')
tree.insert(47)
tree.insert(41)
assert tree.is_valid()

# random_insert(tree)
# assert tree.is_valid()
# tree.insert(-1)
