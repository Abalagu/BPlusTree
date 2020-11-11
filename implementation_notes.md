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
