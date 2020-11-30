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

## On split behavior difference between leaf and internal nodes
https://youtu.be/_nY8yR6iqx4?t=263
When splitting a leaf, copy the middle key value up; when splitting an internal node, move the middle key value up.  The video quotes that a leaf node represents actual data, but an internal node may contain redundant information.  The discussion here demonstrates that the split behavior of internal node is mandatory, not optional, because there is no way that the resulting two internal nodes after split conforms to the constraint while keeping all the keys.     

Suppose the i-th leaf of an internal node `p` overflows after an insertion, and splits to node i_1 and i_2.  The i_1 node retains half of the information of the i-th leaf node, and the i_2 node is newly created to be inserted into its parent.   

The middle key value of a leaf represents an actual data, and should be kept.  Although there are other valid key values to be inserted into the parent keys that do not violate B+Tree rules, such as any value in interval `(max(i_1.keys), min(i_2.keys)+1]`, copying `i_2.keys[0]`, which is the smallest key in i_2 node, would be the easiest to do.    

However, when splitting an internal node, it is forced to leave the middle key value out for insertion to the parent node.
Suppose tree is of order 3, internal nodes pointers between [2,4], keys between [1,3].  Also suppose an internal node `n` of height 1 is already full with 4 pointers and 3 keys, and node `n` is a child node of its parent node `p` at height 2.  Suppose an insertion to one of `n`'s child triggers its split, and node `n` receives a new child, which as a chaining effect makes it split as well.  Notice that now the internal node `n` has 5 pointers and 4 keys.  To properly split the internal node to two groups, the 5 child pointers need to be distributed, see discussion on node distribution of either dense or sparse.  The split of internal node `n` should result in `n_1` with 3 pointers and 2 keys, and `n_2` with 2 pointers and 1 key.  Notice that the total number of keys from `n_1` and `n_2` is 3, which is 1 key short of the 4 keys when `n` is in overflow state.  The missing key is elevated to node `p`, the parent of node `n`.   

## On merge after delete
what if after deletion of a key, the node tries to merge with the neighbor nodes, but all neighbor nodes are full?

## deletion
after deleting a key, if the key appears in the internal nodes as well, one need to update those values as well to make 
why update internal node key values when it does not violate b plus tree rules?

after redistribution, update of internal node keys is necessary because if the min_key is taken from a node, then it messes around with upper layer internal node navigation.  

If neighbor nodes are all half full, then the underflow node cannot borrow from either sides, and has to merge with one of them.
 
 
https://youtu.be/pGOdeCpuwpI?t=672
it seems that an extra rule is enforced, which is to make every key within internal node be a key that exists in the leaf node.  

complicated case concerning deletion of a key: 
the tree may decrease its height by 1, making the tree unbalanced (not having equal height for each leaf)

solution to insufficient keys within a node after deletion: 
1. if neighbor nodes have more than half keys, redistribute to the current one.
2. if neighbor nodes are on the half threshold, try to merge with them.  
redistribution is necessary in deletion, because one cannot merge with neighbor nodes when they are full.  

https://youtu.be/pGOdeCpuwpI?t=760
handling height decrease, by redistributing key from sibling

If a node has insufficient keys after deletion, there are three ways to handle.  
1. try redistribute a sibling key to the node.  This won't work if its left and right siblings are half full.
2. try merge into a sibling node.  This won't work if its left and right siblings are full.
3. It has no left sibling nor right sibling.  In this case the node can only be the root itself, and the child node now elevates to be the new root.  After becoming the root, the key and pointer constraint are lifted.  

It is obvious that in any case, one of the three conditions will be satisfied.  

