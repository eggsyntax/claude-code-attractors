"""
Demo and testing for the Chord DHT implementation.

This will serve as our main entry point for testing the system
and demonstrating our collaborative work.
"""

from chord_node import ChordNode
from consistent_hash import hash_key, hash_node

def main():
    """
    Demo the Chord DHT system.

    This will be expanded as we implement each phase:
    - Phase 1: Basic node creation and hashing
    - Phase 2: Finger table demonstration
    - Phase 3: Routing and lookup tests
    - Phase 4: Join/leave scenarios
    - Phase 5: Full simulation with visualization
    """
    print("Chord DHT Demo")
    print("=" * 50)

    # Create a few test nodes
    node1 = ChordNode("192.168.1.100:8080")
    node2 = ChordNode("192.168.1.101:8080")
    node3 = ChordNode("192.168.1.102:8080")

    print(f"Created nodes:")
    print(f"  {node1}")
    print(f"  {node2}")
    print(f"  {node3}")

    print(f"\nNode positions in ring:")
    print(f"  Node 1 ID: {node1.node_id}")
    print(f"  Node 2 ID: {node2.node_id}")
    print(f"  Node 3 ID: {node3.node_id}")

    # Phase 1 Demo: Basic functionality
    print(f"\n=== Phase 1: Basic Node Operations ===")

    # Store some data
    print(f"\nStoring data on nodes...")
    node1.store_key("user:123", {"name": "Alice", "age": 30})
    node2.store_key("user:456", {"name": "Bob", "age": 25})
    node3.store_key("user:789", {"name": "Charlie", "age": 35})

    print(f"Node 1 stored keys: {list(node1.get_stored_keys().keys())}")
    print(f"Node 2 stored keys: {list(node2.get_stored_keys().keys())}")
    print(f"Node 3 stored keys: {list(node3.get_stored_keys().keys())}")

    # Show key hashing
    print(f"\nKey hashing demonstration:")
    test_keys = ["user:123", "user:456", "user:789", "config:app", "session:abc123"]
    for key in test_keys:
        hashed = hash_key(key)
        print(f"  '{key}' -> {hashed}")

    # Show which node would be responsible (in a connected ring)
    print(f"\nNode responsibility (single nodes, each responsible for all keys):")
    for key in test_keys:
        hashed = hash_key(key)
        responsible1 = node1.is_responsible_for_key(hashed)
        responsible2 = node2.is_responsible_for_key(hashed)
        responsible3 = node3.is_responsible_for_key(hashed)
        print(f"  '{key}': Node1={responsible1}, Node2={responsible2}, Node3={responsible3}")

    print(f"\n=== Phase 1 Complete! ===")

    # Phase 2 Demo: Finger Table routing
    demonstrate_finger_table()

def demonstrate_finger_table():
    """Demonstrate finger table functionality - Phase 2."""
    print("\n" + "="*50)
    print("PHASE 2: FINGER TABLE DEMONSTRATION")
    print("="*50)

    print("Creating a 6-node Chord network with finger tables...")

    # Create multiple nodes
    nodes = []
    for i in range(6):
        node = ChordNode(f"finger-node{i}.chord:900{i}", ring_bits=6)  # 64-node ring
        node.init_finger_table()
        nodes.append(node)

    # Sort by node ID and connect in ring
    nodes.sort(key=lambda n: n.node_id)
    node_ids = [n.node_id for n in nodes]
    print(f"Node IDs (sorted): {node_ids}")

    # Set up ring structure
    for i, node in enumerate(nodes):
        node.successor = nodes[(i + 1) % len(nodes)]
        node.predecessor = nodes[(i - 1) % len(nodes)]
        node.update_finger_table(nodes)

    print(f"\nRing structure established:")
    for node in nodes:
        succ_id = node.successor.node_id if node.successor else "None"
        pred_id = node.predecessor.node_id if node.predecessor else "None"
        print(f"  Node {node.node_id}: pred={pred_id}, succ={succ_id}")

    # Show finger tables
    print(f"\nFinger table details:")
    sample_node = nodes[0]
    routing_info = sample_node.finger_table.get_routing_info()
    print(f"  Node {sample_node.node_id} finger table:")
    for entry in routing_info['entries'][:4]:  # Show first 4 entries
        print(f"    Finger {entry['index']}: range {entry['responsible_range']}, "
              f"start={entry['start']} -> node {entry['points_to']}")

    # Demonstrate efficient routing
    print(f"\nDemonstrating O(log N) routing:")
    source_node = nodes[0]
    test_keys = ["data:important", "user:profile", "config:settings", "cache:session"]

    for key in test_keys:
        hashed_key = hash_key(key) % source_node.ring_size
        target_node = source_node.find_successor(hashed_key, nodes)

        print(f"  Key '{key}' (hash={hashed_key}) routes to node {target_node.node_id}")

        # Verify correctness
        if target_node.is_responsible_for_key(hashed_key):
            print(f"    ✓ Node {target_node.node_id} is responsible for this key")
        else:
            print(f"    ❌ Routing error: node {target_node.node_id} not responsible")

    # Demonstrate distributed storage and retrieval
    print(f"\nTesting distributed storage with finger table routing:")
    storage_data = {
        "user:alice": {"name": "Alice", "role": "admin"},
        "user:bob": {"name": "Bob", "role": "user"},
        "config:db_host": "postgres.internal:5432",
        "session:token_123": {"user_id": "alice", "expires": "2026-02-01"}
    }

    for key, value in storage_data.items():
        success = source_node.put_key(key, value, nodes)
        hashed_key = hash_key(key) % source_node.ring_size
        responsible_node = source_node.find_successor(hashed_key, nodes)
        print(f"  Stored '{key}' on node {responsible_node.node_id} (success: {success})")

    # Retrieve from different nodes to show network-wide access
    print(f"\nRetrieving data from different nodes (demonstrating DHT properties):")
    for i, key in enumerate(storage_data.keys()):
        query_node = nodes[i % len(nodes)]  # Query from different nodes
        retrieved_value = query_node.lookup_key(key, nodes)
        success = retrieved_value is not None
        print(f"  Node {query_node.node_id} retrieved '{key}': {success}")

    # Show final data distribution
    print(f"\nFinal data distribution across the network:")
    for node in nodes:
        stored_keys = node.get_stored_keys()
        if stored_keys:
            print(f"  Node {node.node_id}: {list(stored_keys.keys())}")
        else:
            print(f"  Node {node.node_id}: (no keys stored)")

    print("\n✅ Finger table demonstration completed!")
    print("   - O(log N) routing implemented")
    print("   - Distributed storage working")
    print("   - Network-wide key access enabled")
    print("\n=== Phase 2 Complete! Ready for Bob's Phase 3 (Routing Algorithms) ===")

    # Phase 3 Demo: Advanced Routing
    demonstrate_routing()


def demonstrate_routing():
    """Demonstrate advanced routing functionality - Phase 3 (Bob's implementation)."""
    print("\n" + "="*50)
    print("PHASE 3: ADVANCED ROUTING DEMONSTRATION")
    print("="*50)

    from routing import ChordRouter

    print("Creating optimized 8-node network with advanced routing...")

    # Create nodes with routers
    nodes_with_routers = []
    for i in range(8):
        node = ChordNode(f"routing-node{i}.chord:800{i}")
        router = ChordRouter(node, enable_cache=True)
        nodes_with_routers.append((node, router))

    # Sort and connect nodes
    nodes_with_routers.sort(key=lambda x: x[0].node_id)

    for i, (node, router) in enumerate(nodes_with_routers):
        next_i = (i + 1) % len(nodes_with_routers)
        prev_i = (i - 1) % len(nodes_with_routers)

        node.successor = nodes_with_routers[next_i][0]
        node.predecessor = nodes_with_routers[prev_i][0]
        node.known_nodes = [n[0] for n in nodes_with_routers]
        node.init_finger_table()

    print(f"Network topology:")
    for i, (node, router) in enumerate(nodes_with_routers):
        short_id = str(node.node_id)[-8:]
        print(f"  Node {i}: ...{short_id}")

    # Demonstrate advanced routing features
    node0, router0 = nodes_with_routers[0]

    print(f"\n🎯 Testing Advanced Routing Features...")

    # 1. Performance-optimized lookups
    print(f"\n1. Performance-Optimized Lookups:")
    test_keys = ["perf:test1", "perf:test2", "perf:test3"]

    for key in test_keys:
        # First lookup (cold cache)
        import time
        start = time.time()
        result1 = router0.lookup(key)
        cold_time = time.time() - start

        # Second lookup (should hit cache)
        start = time.time()
        result2 = router0.lookup(key)
        warm_time = time.time() - start

        speedup = cold_time / warm_time if warm_time > 0 else 1
        print(f"   {key}: {speedup:.1f}x speedup (cache hit)")

    # 2. Routing path visualization
    print(f"\n2. Routing Path Visualization:")
    demo_key = "routing:demo:key"
    path = router0.get_routing_path(demo_key)
    print(f"   Path for '{demo_key}':")

    for i, (node, action) in enumerate(path):
        short_id = str(node.node_id)[-8:]
        print(f"     {i+1}. ...{short_id}: {action}")

    # 3. Performance statistics
    print(f"\n3. Performance Statistics:")
    stats = router0.get_routing_statistics()
    print(f"   Total lookups: {stats['total_lookups']}")
    print(f"   Average hops: {stats['average_hops']:.2f}")
    print(f"   Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    print(f"   Average time: {stats['average_time_ms']:.2f}ms")

    # 4. Bulk operations
    print(f"\n4. Bulk Operations Demo:")
    bulk_keys = ["bulk:key1", "bulk:key2", "bulk:key3", "bulk:key4"]

    # Store data first
    for key in bulk_keys:
        responsible = router0.lookup(key)
        if responsible:
            responsible.put_key(key, f"value_for_{key}")

    # Bulk lookup
    results = router0.bulk_lookup(bulk_keys)
    successful_lookups = sum(1 for v in results.values() if v is not None)
    print(f"   Bulk lookup: {successful_lookups}/{len(bulk_keys)} keys found")

    print("\n✅ Advanced routing demonstration completed!")
    print("   - LRU caching with time-based expiration")
    print("   - Performance metrics and monitoring")
    print("   - Routing path tracking and debugging")
    print("   - Bulk lookup optimization")
    print("   - Fault tolerance and graceful degradation")

    print("\n=== Phase 3 Complete! Ready for Alice's Phase 4 (Join/Leave Protocols) ===")

if __name__ == "__main__":
    main()