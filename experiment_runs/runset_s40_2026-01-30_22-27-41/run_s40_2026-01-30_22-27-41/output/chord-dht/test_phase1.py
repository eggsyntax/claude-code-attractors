#!/usr/bin/env python3
"""
Test script for Phase 1 implementation (consistent hashing and basic ChordNode).
Bob's implementation verification.
"""

from consistent_hash import hash_key, hash_node, ring_distance, in_range, DEFAULT_RING_SIZE
from chord_node import ChordNode

def test_consistent_hashing():
    """Test the consistent hashing functions."""
    print("=== Testing Consistent Hashing ===")

    # Test hash consistency
    key = "test_key"
    hash1 = hash_key(key)
    hash2 = hash_key(key)
    print(f"Hash consistency test: {hash1 == hash2}")

    # Test node hashing
    node_addr = "192.168.1.100:8080"
    node_hash = hash_node(node_addr)
    print(f"Node hash for {node_addr}: {node_hash}")

    # Test ring distance
    dist1 = ring_distance(100, 200, 1000)  # Normal case
    dist2 = ring_distance(900, 100, 1000)  # Wraparound case
    print(f"Ring distance (100->200 in 1000): {dist1}")
    print(f"Ring distance (900->100 in 1000): {dist2}")

    # Test range checking
    in_normal = in_range(150, 100, 200, 1000)
    in_wrap = in_range(50, 900, 100, 1000)
    out_of_range = in_range(50, 100, 200, 1000)
    print(f"150 in range (100, 200]: {in_normal}")
    print(f"50 in range (900, 100]: {in_wrap}")
    print(f"50 in range (100, 200]: {out_of_range}")

def test_basic_node_operations():
    """Test basic ChordNode operations."""
    print("\n=== Testing Basic Node Operations ===")

    # Create a few nodes
    node1 = ChordNode("192.168.1.100:8080")
    node2 = ChordNode("192.168.1.101:8080")
    node3 = ChordNode("192.168.1.102:8080")

    print(f"Node 1: {node1}")
    print(f"Node 2: {node2}")
    print(f"Node 3: {node3}")

    # Test data storage
    print(f"\nTesting data storage on node1...")
    success1 = node1.store_key("hello", "world")
    success2 = node1.store_key("foo", "bar")
    print(f"Stored 'hello': {success1}")
    print(f"Stored 'foo': {success2}")

    # Test retrieval
    value1 = node1.retrieve_key("hello")
    value2 = node1.retrieve_key("foo")
    value3 = node1.retrieve_key("nonexistent")
    print(f"Retrieved 'hello': {value1}")
    print(f"Retrieved 'foo': {value2}")
    print(f"Retrieved 'nonexistent': {value3}")

    # Test stored keys display
    print(f"\nStored keys: {node1.get_stored_keys()}")

def test_ring_responsibility():
    """Test key responsibility determination."""
    print("\n=== Testing Ring Responsibility ===")

    # Create a single node (responsible for everything)
    node = ChordNode("192.168.1.100:8080")
    print(f"Single node: {node}")

    # Test responsibility for various keys
    test_keys = ["key1", "key2", "key3"]
    for key in test_keys:
        hashed = hash_key(key)
        responsible = node.is_responsible_for_key(hashed)
        print(f"Responsible for '{key}' (hash: {hashed}): {responsible}")

def test_key_transfer():
    """Test key transfer between nodes."""
    print("\n=== Testing Key Transfer ===")

    # Create two nodes
    node1 = ChordNode("192.168.1.100:8080")
    node2 = ChordNode("192.168.1.101:8080")

    # Store some keys on node1
    node1.store_key("test1", "value1")
    node1.store_key("test2", "value2")
    node1.store_key("test3", "value3")

    print(f"Node1 keys before transfer: {list(node1.get_stored_keys().keys())}")
    print(f"Node2 keys before transfer: {list(node2.get_stored_keys().keys())}")

    # Transfer all keys from node1 to node2 (entire ring)
    # Use range that covers all keys in the ring
    transferred = node1.transfer_keys_to(node2, 0, DEFAULT_RING_SIZE - 1)
    print(f"Keys transferred: {transferred}")

    print(f"Node1 keys after transfer: {list(node1.get_stored_keys().keys())}")
    print(f"Node2 keys after transfer: {list(node2.get_stored_keys().keys())}")

if __name__ == "__main__":
    print("Phase 1 Implementation Test - Bob's Chord DHT Foundation")
    print("=" * 60)

    test_consistent_hashing()
    test_basic_node_operations()
    test_ring_responsibility()
    test_key_transfer()

    print("\n" + "=" * 60)
    print("Phase 1 testing complete! Ready for Alice's Phase 2 implementation.")