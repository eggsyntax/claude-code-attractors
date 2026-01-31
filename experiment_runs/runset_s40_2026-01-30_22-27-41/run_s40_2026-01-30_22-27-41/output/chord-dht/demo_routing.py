#!/usr/bin/env python3
"""
Comprehensive demonstration of Bob's Phase 3 routing system.

This showcases all the advanced routing features:
- O(log N) lookups with finger tables
- Routing cache optimization
- Performance metrics
- Range queries and bulk operations
- Routing path visualization
"""

import time
from chord_node import ChordNode
from routing import ChordRouter
from consistent_hash import hash_key


def create_chord_network(size=8):
    """Create a Chord network with the specified number of nodes."""
    print(f"🏗️  Creating Chord network with {size} nodes...")

    # Create nodes
    nodes_with_routers = []
    for i in range(size):
        node = ChordNode(f"node_{i}")
        router = ChordRouter(node, enable_cache=True)
        nodes_with_routers.append((node, router))

    # Sort by node ID for proper ring construction
    nodes_with_routers.sort(key=lambda x: x[0].node_id)

    # Build the ring
    for i, (node, router) in enumerate(nodes_with_routers):
        next_i = (i + 1) % len(nodes_with_routers)
        prev_i = (i - 1) % len(nodes_with_routers)

        node.successor = nodes_with_routers[next_i][0]
        node.predecessor = nodes_with_routers[prev_i][0]

        # Set known nodes for finger table construction
        node.known_nodes = [n[0] for n in nodes_with_routers]
        node.init_finger_table()

    print(f"✅ Network created with ring:")
    for i, (node, router) in enumerate(nodes_with_routers):
        print(f"   Node {i}: ID {node.node_id}")

    return nodes_with_routers


def demo_basic_routing(network):
    """Demonstrate basic routing functionality."""
    print(f"\n📍 === Basic Routing Demo ===")

    node0, router0 = network[0]

    # Store some test data
    test_data = [
        ("user:alice", "Alice's profile data"),
        ("user:bob", "Bob's profile data"),
        ("document:readme", "Project documentation"),
        ("config:database", "DB connection string"),
        ("session:xyz123", "User session data")
    ]

    print(f"📝 Storing {len(test_data)} items across the network...")
    for key, value in test_data:
        responsible_node = router0.lookup(key)
        if responsible_node:
            responsible_node.put_key(key, value)
            print(f"   {key} -> Node {responsible_node.node_id}")

    print(f"\n🔍 Retrieving items from any node in the network...")
    for key, expected_value in test_data:
        responsible_node = router0.lookup(key)
        if responsible_node:
            stored_keys = responsible_node.get_stored_keys()
            actual_value = stored_keys.get(key, "NOT_FOUND")
            status = "✅" if actual_value == expected_value else "❌"
            print(f"   {status} {key}: {actual_value}")


def demo_routing_paths(network):
    """Demonstrate routing path visualization."""
    print(f"\n🛤️  === Routing Path Visualization ===")

    node0, router0 = network[0]

    test_keys = ["path_test_1", "path_test_2", "long_path_test"]

    for key in test_keys:
        print(f"\n🎯 Routing path for '{key}':")
        path = router0.get_routing_path(key)

        for i, (node, action) in enumerate(path):
            short_id = str(node.node_id)[-6:]  # Last 6 digits for readability
            print(f"   {i+1}. Node ...{short_id}: {action}")

        # Show final hop count
        final_hops = len([p for p in path if "ROUTE_VIA" in p[1]])
        print(f"   → Total routing hops: {final_hops}")


def demo_performance_optimization(network):
    """Demonstrate caching and performance optimization."""
    print(f"\n⚡ === Performance & Caching Demo ===")

    node0, router0 = network[0]

    # Create a set of keys for testing
    test_keys = [f"perf_key_{i}" for i in range(10)]

    # First pass - populate cache
    print(f"🏃 First pass (cold cache):")
    start_time = time.time()
    for key in test_keys:
        router0.lookup(key)
    cold_time = time.time() - start_time

    # Second pass - should hit cache
    print(f"🏃‍♀️ Second pass (warm cache):")
    start_time = time.time()
    for key in test_keys:
        router0.lookup(key)
    warm_time = time.time() - start_time

    # Show performance statistics
    stats = router0.get_routing_statistics()
    print(f"\n📊 Performance Statistics:")
    print(f"   Total lookups: {stats['total_lookups']}")
    print(f"   Average hops: {stats['average_hops']:.2f}")
    print(f"   Average time: {stats['average_time_ms']:.2f}ms")
    print(f"   Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    print(f"   Cache size: {stats['cache_size']} entries")
    print(f"   Cold cache time: {cold_time*1000:.2f}ms")
    print(f"   Warm cache time: {warm_time*1000:.2f}ms")
    print(f"   Speedup: {cold_time/warm_time:.2f}x")


def demo_advanced_queries(network):
    """Demonstrate range queries and bulk operations."""
    print(f"\n🔎 === Advanced Queries Demo ===")

    node0, router0 = network[0]

    # Store data with keys that have interesting hash ranges
    print(f"📝 Storing test dataset...")
    test_data = {
        "apple": "red fruit",
        "banana": "yellow fruit",
        "cherry": "small red fruit",
        "date": "brown fruit",
        "elderberry": "dark purple fruit",
        "fig": "sweet fruit",
        "grape": "cluster fruit"
    }

    for key, value in test_data.items():
        responsible_node = router0.lookup(key)
        if responsible_node:
            responsible_node.put_key(key, value)

    # Demonstrate bulk lookup
    print(f"\n📦 Bulk lookup test:")
    lookup_keys = ["apple", "cherry", "elderberry", "nonexistent_key"]
    results = router0.bulk_lookup(lookup_keys)

    for key in lookup_keys:
        value = results.get(key, "NOT_FOUND")
        status = "✅" if value != "NOT_FOUND" and value is not None else "❌"
        print(f"   {status} {key}: {value}")

    # Demonstrate range query
    print(f"\n📏 Range query test (a-d):")
    range_results = router0.range_query("a", "d")
    print(f"   Found {len(range_results)} items in range:")
    for key, value in range_results[:5]:  # Show first 5 results
        print(f"   - {key}: {value}")


def demo_fault_tolerance(network):
    """Demonstrate routing fault tolerance."""
    print(f"\n🛡️  === Fault Tolerance Demo ===")

    if len(network) < 4:
        print("   Skipping fault tolerance demo (need at least 4 nodes)")
        return

    node0, router0 = network[0]

    # Test routing with incomplete finger tables
    print(f"🔧 Testing routing with degraded finger tables...")

    # Clear some finger tables to simulate network issues
    for i in range(2, min(4, len(network))):
        node, router = network[i]
        if node.finger_table:
            # Simulate partial finger table failure
            node.finger_table.entries = node.finger_table.entries[:3]

    # Test if routing still works
    test_key = "fault_tolerance_test"
    result = router0.lookup(test_key)

    if result:
        print(f"   ✅ Routing succeeded despite degraded finger tables")
        print(f"   Found responsible node: ...{str(result.node_id)[-6:]}")

        # Show routing path
        path = router0.get_routing_path(test_key)
        print(f"   Routing path:")
        for i, (node, action) in enumerate(path):
            short_id = str(node.node_id)[-6:]
            print(f"     {i+1}. ...{short_id}: {action}")
    else:
        print(f"   ❌ Routing failed with degraded network")

    # Restore finger tables
    print(f"🔄 Restoring network...")
    for node, router in network:
        node.init_finger_table()

    print(f"   ✅ Network restored")


def run_routing_demo():
    """Run the complete routing demonstration."""
    print("🚀 Chord DHT Advanced Routing System Demo")
    print("="*60)
    print("Bob's Phase 3 Implementation - Showcasing:")
    print("• O(log N) lookups with finger table optimization")
    print("• LRU caching for performance improvement")
    print("• Routing path visualization and debugging")
    print("• Range queries and bulk operations")
    print("• Performance metrics and monitoring")
    print("• Fault tolerance and graceful degradation")

    # Create the network
    network = create_chord_network(size=8)

    # Run all demonstrations
    demo_basic_routing(network)
    demo_routing_paths(network)
    demo_performance_optimization(network)
    demo_advanced_queries(network)
    demo_fault_tolerance(network)

    print(f"\n🎉 Routing demonstration complete!")
    print(f"\nPhase 3 Summary - Advanced Routing Features:")
    print(f"✅ O(log N) lookups using finger table routing")
    print(f"✅ LRU cache with time-based expiration")
    print(f"✅ Comprehensive performance metrics")
    print(f"✅ Routing path tracking and visualization")
    print(f"✅ Range queries for key range operations")
    print(f"✅ Bulk lookup optimization")
    print(f"✅ Fault tolerance with graceful degradation")
    print(f"✅ Cache invalidation and optimization triggers")

    print(f"\n👥 Ready for Alice's Phase 4 - Join/Leave Protocols!")


if __name__ == "__main__":
    run_routing_demo()