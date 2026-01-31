#!/usr/bin/env python3

from chord_node import ChordNode
from routing import ChordRouter
from consistent_hash import hash_key

# Create a simple two-node network
node1 = ChordNode("node1")
node2 = ChordNode("node2")

# Set up ring
if node1.node_id < node2.node_id:
    node1.successor = node2
    node1.predecessor = node2
    node2.successor = node1
    node2.predecessor = node1
else:
    node2.successor = node1
    node2.predecessor = node1
    node1.successor = node2
    node1.predecessor = node2

# Setup known nodes and finger tables
node1.known_nodes = [node1, node2]
node2.known_nodes = [node1, node2]
node1.init_finger_table()
node2.init_finger_table()

# Create router and test
router1 = ChordRouter(node1)

print(f"Node 1 ID: {node1.node_id}")
print(f"Node 2 ID: {node2.node_id}")

test_key = "test123"
key_id = hash_key(test_key)
print(f"Key '{test_key}' hashes to: {key_id}")

# Check who should be responsible
print(f"Node 1 responsible: {node1.is_responsible_for_key(key_id)}")
print(f"Node 2 responsible: {node2.is_responsible_for_key(key_id)}")

# Test routing
result = router1.lookup(test_key)
if result:
    print(f"Router found responsible node: {result.node_id}")
    print(f"Storing key on this node...")
    result.put_key(test_key, "test_value")
    # Check if key exists
    stored_keys = result.get_stored_keys()
    if test_key in stored_keys:
        print(f"Retrieved value: {stored_keys[test_key]}")
    else:
        print("Key not found in storage")
else:
    print("No responsible node found")

# Check routing path
path = router1.get_routing_path(test_key)
print(f"\nRouting path:")
for i, (node, action) in enumerate(path):
    print(f"  {i+1}. Node {node.node_id}: {action}")