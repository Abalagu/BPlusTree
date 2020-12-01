# Created by Luming on 11/26/2020 8:15 PM
from typing import List

import numpy as np

from BPlusTree import BPlusTree
from test_functions import *

# use gen_trivial_tree, and call insert, delete, search, range_search on it.
# use tree.is_valid(), or node.is_valid() to check for consistency before and after the operation
# use node.print_layer() to print out the tree rooted under the given node,
# or tree.print_layer() to print out the whole b plus tree
if __name__ == '__main__':
    tree = gen_trivial_tree(3, 20, 'dense')
