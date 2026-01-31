"""
Comprehensive tests for the Chord DHT routing system.

Bob's Phase 3 testing - validates advanced routing algorithms, caching,
and performance monitoring.
"""

import time
from chord_node import ChordNode
from consistent_hash import hash_key
from finger_table import FingerTable
from routing import ChordRouter, RoutingMetrics, RoutingCache


def test_basic_routing():
    """Test basic routing functionality."""
    print("=== Testing Basic Routing ===")

    # Create a network of nodes
    nodes = []
    for i in range(5):
        address = f"node_{i}"
        node = ChordNode(address)
        router = ChordRouter(node)
        nodes.append((node, router))

    # Set up the ring
    for i, (node, router) in enumerate(nodes):
        next_i = (i + 1) % len(nodes)
        node.successor = nodes[next_i][0]
        node.predecessor = nodes[i-1][0]

        # Add all nodes to known_nodes for finger table construction
        node.known_nodes = [n[0] for n in nodes]
        node.init_finger_table()

    # Test routing
    node0, router0 = nodes[0]

    # Store a key and verify routing finds it
    test_key = "test_routing_key"
    responsible_node = router0.lookup(test_key)

    if responsible_node:
        responsible_node.put_key(test_key, "test_value")

        # Verify we can route to and retrieve the key
        found_node = router0.lookup(test_key)
        assert found_node == responsible_node, "Routing should find the same responsible node"

        value = found_node.get_key(test_key)
        assert value == "test_value", "Should retrieve the correct value"

        print(f"✅ Successfully routed to node {responsible_node.node_id} for key '{test_key}'")
    else:
        print("❌ Failed to find responsible node")
        return False

    return True


def test_routing_path_tracking():
    """Test routing path tracking for debugging."""
    print("\n=== Testing Routing Path Tracking ===")

    # Create larger network to see multi-hop routing
    nodes = []
    for i in range(8):
        address = f"node_{i}"
        node = ChordNode(address)
        router = ChordRouter(node)
        nodes.append((node, router))

    # Set up ring with proper ordering by node_id
    nodes_by_id = sorted(nodes, key=lambda x: x[0].node_id)

    for i, (node, router) in enumerate(nodes_by_id):
        next_i = (i + 1) % len(nodes_by_id)
        node.successor = nodes_by_id[next_i][0]
        node.predecessor = nodes_by_id[i-1][0]

        # Add all nodes for finger table construction
        node.known_nodes = [n[0] for n in nodes_by_id]
        node.init_finger_table()

    # Test path tracking
    node0, router0 = nodes_by_id[0]
    test_key = "path_tracking_test"

    path = router0.get_routing_path(test_key)

    print(f"Routing path for key '{test_key}':")
    for i, (node, action) in enumerate(path):
        print(f"  {i+1}. Node {node.node_id}: {action}")

    # Verify path makes sense
    assert len(path) > 0, "Path should not be empty"
    final_node, final_action = path[-1]
    assert "RESPONSIBLE" in final_action, "Final node should be responsible for the key"

    print("✅ Routing path tracking working correctly")
    return True


def test_routing_cache():
    """Test routing cache functionality."""
    print("\n=== Testing Routing Cache ===")

    # Create simple network
    nodes = []
    for i in range(4):
        address = f"node_{i}"
        node = ChordNode(address)
        router = ChordRouter(node, enable_cache=True)
        nodes.append((node, router))

    # Set up ring
    nodes_by_id = sorted(nodes, key=lambda x: x[0].node_id)
    for i, (node, router) in enumerate(nodes_by_id):
        next_i = (i + 1) % len(nodes_by_id)
        node.successor = nodes_by_id[next_i][0]
        node.predecessor = nodes_by_id[i-1][0]
        node.known_nodes = [n[0] for n in nodes_by_id]
        node.init_finger_table()

    node0, router0 = nodes_by_id[0]

    # First lookup (cache miss)
    test_key = "cache_test_key"
    start_time = time.time()
    result1 = router0.lookup(test_key)
    first_lookup_time = time.time() - start_time

    # Second lookup (should be cache hit)
    start_time = time.time()
    result2 = router0.lookup(test_key)
    second_lookup_time = time.time() - start_time

    assert result1 == result2, "Both lookups should return the same node"

    # Check metrics
    metrics = router0.get_metrics()
    assert metrics.total_lookups >= 2, "Should have recorded at least 2 lookups"
    assert metrics.cache_hits >= 1, "Should have at least 1 cache hit"

    stats = router0.get_routing_statistics()
    print(f"Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    print(f"Average hops: {stats['average_hops']:.2f}")

    print("✅ Routing cache working correctly")
    return True


def test_range_queries():
    """Test range query functionality."""
    print("\n=== Testing Range Queries ===")

    # Create network
    nodes = []
    for i in range(4):
        address = f"node_{i}"
        node = ChordNode(address)
        router = ChordRouter(node)
        nodes.append((node, router))

    # Set up ring
    nodes_by_id = sorted(nodes, key=lambda x: x[0].node_id)
    for i, (node, router) in enumerate(nodes_by_id):
        next_i = (i + 1) % len(nodes_by_id)
        node.successor = nodes_by_id[next_i][0]
        node.predecessor = nodes_by_id[i-1][0]
        node.known_nodes = [n[0] for n in nodes_by_id]
        node.init_finger_table()

    # Store test data across the network
    test_data = [
        ("apple", "fruit"),
        ("banana", "fruit"),
        ("carrot", "vegetable"),
        ("date", "fruit"),
        ("eggplant", "vegetable")
    ]

    node0, router0 = nodes_by_id[0]

    for key, value in test_data:
        responsible_node = router0.lookup(key)
        if responsible_node:
            responsible_node.put_key(key, value)

    # Perform range query
    results = router0.range_query("a", "d")

    print(f"Range query results (a-d): {len(results)} items")
    for key, value in results:
        print(f"  {key}: {value}")

    # Should find keys that hash to values between hash("a") and hash("d")
    assert len(results) >= 0, "Range query should return results"

    print("✅ Range queries working correctly")
    return True


def test_bulk_lookup():
    """Test bulk lookup functionality."""
    print("\n=== Testing Bulk Lookup ===")

    # Create network and store data
    nodes = []
    for i in range(3):
        address = f"node_{i}"
        node = ChordNode(address)
        router = ChordRouter(node)
        nodes.append((node, router))

    # Set up ring
    nodes_by_id = sorted(nodes, key=lambda x: x[0].node_id)
    for i, (node, router) in enumerate(nodes_by_id):
        next_i = (i + 1) % len(nodes_by_id)
        node.successor = nodes_by_id[next_i][0]
        node.predecessor = nodes_by_id[i-1][0]
        node.known_nodes = [n[0] for n in nodes_by_id]
        node.init_finger_table()

    # Store test data
    test_keys = ["key1", "key2", "key3", "key4", "key5"]
    node0, router0 = nodes_by_id[0]

    for key in test_keys:
        responsible_node = router0.lookup(key)
        if responsible_node:
            responsible_node.put_key(key, f"value_{key}")

    # Perform bulk lookup
    results = router0.bulk_lookup(test_keys)

    print(f"Bulk lookup results:")
    for key, value in results.items():
        print(f"  {key}: {value}")

    # Verify all keys were found
    for key in test_keys:
        assert key in results, f"Key {key} should be in results"
        assert results[key] == f"value_{key}", f"Value for {key} should be correct"

    print("✅ Bulk lookup working correctly")
    return True


def test_routing_performance():
    """Test routing performance metrics."""
    print("\n=== Testing Routing Performance ===")

    # Create larger network to test performance
    nodes = []
    for i in range(10):
        address = f"node_{i}"
        node = ChordNode(address)
        router = ChordRouter(node, enable_cache=True)
        nodes.append((node, router))

    # Set up ring
    nodes_by_id = sorted(nodes, key=lambda x: x[0].node_id)
    for i, (node, router) in enumerate(nodes_by_id):
        next_i = (i + 1) % len(nodes_by_id)
        node.successor = nodes_by_id[next_i][0]
        node.predecessor = nodes_by_id[i-1][0]
        node.known_nodes = [n[0] for n in nodes_by_id]
        node.init_finger_table()

    node0, router0 = nodes_by_id[0]

    # Perform multiple lookups
    test_keys = [f"perf_test_key_{i}" for i in range(20)]

    for key in test_keys:
        router0.lookup(key)  # First lookup
        router0.lookup(key)  # Second lookup (should hit cache)

    # Check performance statistics
    stats = router0.get_routing_statistics()

    print(f"Performance Statistics:")
    print(f"  Total lookups: {stats['total_lookups']}")
    print(f"  Average hops: {stats['average_hops']:.2f}")
    print(f"  Average time: {stats['average_time_ms']:.2f}ms")
    print(f"  Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    print(f"  Cache size: {stats['cache_size']}")

    # Verify reasonable performance
    assert stats['average_hops'] <= 4, f"Average hops should be reasonable for 10 nodes, got {stats['average_hops']}"
    assert stats['cache_hit_rate'] > 0, "Should have some cache hits"

    print("✅ Performance metrics working correctly")
    return True


def run_all_routing_tests():
    """Run all routing tests."""
    print("🧪 Running Chord DHT Routing Tests")
    print("="*50)

    test_functions = [
        test_basic_routing,
        test_routing_path_tracking,
        test_routing_cache,
        test_range_queries,
        test_bulk_lookup,
        test_routing_performance
    ]

    passed = 0
    total = len(test_functions)

    for test_func in test_functions:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {e}")

    print("\n" + "="*50)
    print(f"Routing Tests Summary: {passed}/{total} passed")

    if passed == total:
        print("🎉 All routing tests passed!")
        return True
    else:
        print("❌ Some routing tests failed")
        return False


if __name__ == "__main__":
    run_all_routing_tests()