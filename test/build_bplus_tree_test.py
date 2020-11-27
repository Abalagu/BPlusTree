# Created by Luming on 11/11/2020 1:47 PM
from BPlusTree import BPlusTree
from data_generation import gen_record

key_range = range(100000, 200000)
num_record = 10000
samples = gen_record(key_range, num_record)

order = 13
tree = BPlusTree(order, keys=samples)
# ret = tree.range_search(123456, 156789)
