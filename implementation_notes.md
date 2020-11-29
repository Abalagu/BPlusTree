<!-- Created by Luming on 11/10/2020 2:05 PM -->

within a b plus tree node, store keys and pointers separately

when the whole b plus tree has only one root node, it serves as a leaf node, no pointers required for each inserted value.

if pointers list is empty, then it is a 

Attributes based on node type:
* root with height as 1 (single root node tree)
    * keys
    * payload
    
* root with height greater than 1
    * keys: int
    * pointers: int
    
* internal nodes
    * keys: int
    * pointers: Node

* leaf nodes
    * keys: int
    * payload: Any.  
        In this application supply artificial payload as the string of key value, 
    * sequence_pointer: Node
    
    
set sequence pointer between child nodes after adding all the nodes to their parent.

use hex(id) to print out the memory address of the object
use this to check if sequence pointer is used correctly.

it seems that treating single node root as leaf would simplify the code.

for each node, #pointers = #keys + 1
p k p k p
with same index, pointers[idx] points to nodes with value smaller than keys[idx]

# construct b plus tree from given list of values
## General issues
https://youtu.be/_nY8yR6iqx4?t=248
when splitting a leaf, copy the middle value up.
when splitting an internal node, move the middle value up.


An internal node of height >= 2 should have its key value from: self.keys[i] = self.pointers[i+1].pointers[0].keys[0]
Otherwise, there would be a missing interval not covered during search, and it can only be mitigated. 
See case: order=3, num_nodes=13, the root key value is the focus.
 
If search continues through the sequence pointer to the next node.  In this case, one cannot determine whether 
a node should contain the value, and can only be certain when it continues right-ward, and a larger value is found while
 the target key is not found.
 
## Dense B Plus Tree
Suppose a list of values with length k are provided, and the b plus tree to be constructed is of order n.  
There must be ceil(k/n) leaf nodes to hold all the values.
Suppose f = ceil(k/n) as the number of leaf nodes, then there are p1 = f - 1 parent nodes.
parent node of key i contains first value of leaf node i+1
If p1 > n, then divide p1 to multiple nodes, p2 = ceil(p1/n) nodes.
Repeat such process, till pi <= n, then treat pi as the root node of the constructed b plus tree.

When constructing dense B+ Trees, one problem arise if the given keys are divided in the above discussed way.  
Suppose order=3, and 7 keys are provided.  The tree that meets the constraint would have leaf nodes distributed as 3+2+2, rather than 3+3+1.  Therefore, when making leaf nodes as full as possible, one should also consider accommodating for the last node.     

Strategy: suppose the number of remaining keys are n.  If order <= n < 2*order, then  


A node split can only happen when it overflows.  If it tries to split when it is exactly full, then the resulting two node will not have sufficient keys to conform to the minimal key constraint.

When taking order as an odd number, the ceiling and flooring operators can be removed from the constraint.

## Biasing of a b plus tree
Left biasing: when the node overflows after an insertion, it splits to two nodes, such that left has more keys than the right.
Right biasing: when splitting, right has more keys than the left.
When making a sparse tree, the left is as sparse as possible, which is right biased; 
when making a dense tree, the left is as full as possible, which is left biased.


## Sparse B Plus Tree

cases: 
order of 3

## split
example: order=3, full tree that triggers overflow on insert
full internal node: 3 keys, 4 pointers.  After leaf overflow, a new leaf node is inserted into the internal node,
making a total of 4 keys, 5 pointers.  The split should result in two nodes, Node(keys[:2], pointers[:3]), Node([3:], pointers[3:])

the node value should be the left-most child first key from its right tree.
self.key[i] = self.pointers[i+1].first_child.keys[0]

# Data Generation
use np.random.choice() to generate random data.
set replace=False to get unique elements within the list.

