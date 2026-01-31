#!/usr/bin/env python3
"""
Interactive Demo of Chord DHT Dynamic Network - Phase 4 Demo

This demo showcases the complete join/leave protocol system with a
visual representation of how the network evolves over time.
"""

import sys
import os
import time
import random

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chord_node import ChordNode
from protocols import JoinLeaveProtocols
from consistent_hash import hash_key


def print_network_state(network, title="Network State"):
    """Print current network state with visual representation"""
    print(f"\n🔍 {title}")
    print("-" * 50)

    if not network:
        print("   📭 Network is empty")
        return

    # Sort nodes by ID for consistent display
    sorted_nodes = sorted(network, key=lambda n: n.node_id)

    print(f"   📊 Network size: {len(network)} nodes")
    print("   🔗 Ring structure:")

    for i, node in enumerate(sorted_nodes):
        # Show node info
        successor_id = node.successor.node_id if node.successor else "None"
        predecessor_id = node.predecessor.node_id if node.predecessor else "None"

        print(f"      [{i+1}] {node.address}")
        print(f"          ID: {node.node_id}")
        print(f"          Keys: {len(node.data)}")
        print(f"          Successor: {successor_id}")
        print(f"          Predecessor: {predecessor_id}")

        # Show stored keys (first few)
        if node.data:
            key_samples = list(node.data.keys())[:3]
            print(f"          Data samples: {key_samples}")
        print()


def simulate_realistic_scenario():
    """Simulate a realistic dynamic network scenario"""
    print("🌐 Chord DHT Dynamic Network Demo")
    print("=" * 50)
    print("This demo simulates a distributed hash table handling")
    print("real-world scenarios with nodes joining and leaving.")

    protocols = JoinLeaveProtocols()
    network = []

    # Phase 1: Build initial network
    print("\n📍 Phase 1: Building Initial Network")
    print("Creating a stable foundation with 3 nodes...")

    initial_nodes = []
    for i in range(3):
        node = ChordNode(f"server-{i+1}.example.com")
        result = protocols.join_node(node, network)
        print(f"   ✅ {node.address} joined")
        print(f"      Network size: {result['network_size_after']}")
        initial_nodes.append(node)

    print_network_state(network, "Initial Network")

    # Phase 2: Add application data
    print("\n📦 Phase 2: Populating with Application Data")
    print("Simulating a web application storing user sessions, configs, and cache...")

    application_data = {
        # User sessions
        "session:user123": {"user_id": "123", "login_time": "2026-01-30T10:00:00Z", "ip": "192.168.1.100"},
        "session:user456": {"user_id": "456", "login_time": "2026-01-30T10:15:00Z", "ip": "192.168.1.101"},
        "session:user789": {"user_id": "789", "login_time": "2026-01-30T10:30:00Z", "ip": "192.168.1.102"},

        # Configuration data
        "config:database_url": "postgresql://localhost:5432/app",
        "config:cache_ttl": 3600,
        "config:max_connections": 100,
        "config:debug_mode": False,

        # Cache entries
        "cache:user_profile_123": {"name": "Alice Johnson", "email": "alice@example.com", "role": "admin"},
        "cache:user_profile_456": {"name": "Bob Smith", "email": "bob@example.com", "role": "user"},
        "cache:api_response_weather": {"temp": 22, "humidity": 65, "cached_at": "2026-01-30T10:00:00Z"},

        # Application metrics
        "metrics:requests_per_minute": 1250,
        "metrics:error_rate": 0.02,
        "metrics:avg_response_time": 45.2,
    }

    # Store data through different nodes to test routing
    nodes_for_storage = network.copy()
    for i, (key, value) in enumerate(application_data.items()):
        storage_node = nodes_for_storage[i % len(nodes_for_storage)]
        storage_node.put_key(key, value)
        print(f"   📝 Stored '{key}' via {storage_node.address}")

    print_network_state(network, "Network After Data Population")

    # Phase 3: Verify data accessibility
    print("\n🔍 Phase 3: Testing Data Accessibility")
    print("Verifying all data is accessible from any node...")

    test_node = network[0]
    accessible_count = 0

    for key in application_data.keys():
        try:
            value = test_node.lookup_key(key)
            if value is not None:
                accessible_count += 1
                print(f"   ✅ '{key}' accessible")
            else:
                print(f"   ❌ '{key}' not found")
        except Exception as e:
            print(f"   ❌ Error accessing '{key}': {e}")

    print(f"\n   📊 Accessibility: {accessible_count}/{len(application_data)} keys accessible")

    # Phase 4: Scale up - nodes joining
    print("\n🔄 Phase 4: Scaling Up - New Nodes Joining")
    print("Simulating traffic increase requiring additional capacity...")

    new_nodes = [
        ChordNode("server-4.example.com"),
        ChordNode("server-5.example.com")
    ]

    for node in new_nodes:
        print(f"\n   ⬆️ {node.address} requesting to join...")
        result = protocols.join_node(node, network)

        print(f"      ✅ Join successful: {result['success']}")
        print(f"      🔄 Keys transferred: {result['keys_transferred']}")
        print(f"      📊 Network size: {result['network_size_before']} → {result['network_size_after']}")
        print(f"      🔧 Nodes stabilized: {result['nodes_stabilized']}")

    print_network_state(network, "Network After Scale-Up")

    # Verify data integrity after joins
    print("\n🔍 Data Integrity Check After Scale-Up")
    accessible_after_join = 0
    for key in application_data.keys():
        for node in network:
            try:
                value = node.lookup_key(key)
                if value is not None:
                    accessible_after_join += 1
                    break
            except:
                continue

    print(f"   📊 Data integrity: {accessible_after_join}/{len(application_data)} keys still accessible")

    # Phase 5: Maintenance - node leaving
    print("\n🔄 Phase 5: Maintenance - Planned Node Departure")
    print("Simulating planned maintenance on one server...")

    maintenance_node = network[2] if len(network) > 2 else network[0]
    print(f"\n   ⬇️ {maintenance_node.address} scheduled for maintenance...")
    print(f"      📦 Keys to migrate: {len(maintenance_node.data)}")

    result = protocols.leave_node(maintenance_node, network)

    print(f"      ✅ Departure successful: {result['success']}")
    print(f"      🔄 Keys transferred: {result['keys_transferred']}")
    print(f"      📊 Network size: {result['network_size_before']} → {result['network_size_after']}")
    print(f"      🔧 Nodes stabilized: {result['nodes_stabilized']}")

    print_network_state(network, "Network After Maintenance")

    # Final data integrity check
    print("\n🔍 Final Data Integrity Verification")
    final_accessible = 0
    missing_keys = []

    for key in application_data.keys():
        found = False
        for node in network:
            try:
                value = node.lookup_key(key)
                if value is not None:
                    found = True
                    final_accessible += 1
                    break
            except:
                continue

        if not found:
            missing_keys.append(key)

    print(f"   📊 Final integrity: {final_accessible}/{len(application_data)} keys accessible")
    if missing_keys:
        print(f"   ⚠️ Missing keys: {missing_keys}")
    else:
        print("   🎉 All data preserved through dynamic operations!")

    # Phase 6: Performance demonstration
    print("\n⚡ Phase 6: Performance Characteristics")
    print("Demonstrating efficient routing in the final network...")

    # Test lookup performance with different starting nodes
    test_keys = list(application_data.keys())[:5]

    for key in test_keys:
        print(f"\n   🔍 Looking up '{key}':")
        for i, node in enumerate(network[:3]):  # Test from first 3 nodes
            try:
                start_time = time.time()
                value = node.lookup_key(key)
                lookup_time = (time.time() - start_time) * 1000  # Convert to ms

                if value is not None:
                    print(f"      Via {node.address}: Found in {lookup_time:.2f}ms")
                else:
                    print(f"      Via {node.address}: Not found")
            except Exception as e:
                print(f"      Via {node.address}: Error - {e}")

    # Network stabilization demo
    print("\n🔧 Phase 7: Network Stabilization")
    print("Running network-wide stabilization to optimize routing...")

    stab_result = protocols.stabilize_network(network)
    print(f"   🔧 Nodes stabilized: {stab_result['nodes_stabilized']}")
    print(f"   🔗 Successor updates: {stab_result['total_successor_updates']}")
    print(f"   🔙 Predecessor updates: {stab_result['total_predecessor_updates']}")
    print(f"   👆 Finger table updates: {stab_result['total_finger_updates']}")
    print(f"   📦 Keys rebalanced: {stab_result['total_keys_transferred']}")

    # Final summary
    print(f"\n🎯 Demo Complete!")
    print("=" * 50)
    print(f"   🌐 Final network size: {len(network)} nodes")
    print(f"   📦 Total keys stored: {sum(len(node.data) for node in network)}")
    print(f"   ✅ Data integrity: {final_accessible}/{len(application_data)} keys preserved")
    print(f"   🚀 Network demonstrates:")
    print(f"      - Dynamic scaling (join/leave)")
    print(f"      - Data consistency during topology changes")
    print(f"      - Efficient routing and lookup")
    print(f"      - Automatic load balancing")
    print(f"      - Self-healing through stabilization")

    return network


def interactive_demo():
    """Run an interactive demo where users can control operations"""
    print("🎮 Interactive Chord DHT Demo")
    print("=" * 30)
    print("Commands: join, leave, put, get, status, stabilize, quit")

    protocols = JoinLeaveProtocols()
    network = []

    while True:
        try:
            cmd = input("\n> ").strip().lower()

            if cmd == "quit" or cmd == "exit":
                break

            elif cmd == "join":
                name = input("Node name: ").strip()
                if name:
                    node = ChordNode(name)
                    result = protocols.join_node(node, network)
                    print(f"Join result: {result}")

            elif cmd == "leave":
                if not network:
                    print("Network is empty")
                    continue

                print("Available nodes:")
                for i, node in enumerate(network):
                    print(f"  {i}: {node.address}")

                try:
                    idx = int(input("Node index to remove: "))
                    if 0 <= idx < len(network):
                        node = network[idx]
                        result = protocols.leave_node(node, network)
                        print(f"Leave result: {result}")
                    else:
                        print("Invalid index")
                except ValueError:
                    print("Invalid input")

            elif cmd == "put":
                if not network:
                    print("Network is empty")
                    continue

                key = input("Key: ").strip()
                value = input("Value: ").strip()

                if key and value:
                    network[0].put_key(key, value)
                    print(f"Stored {key} = {value}")

            elif cmd == "get":
                if not network:
                    print("Network is empty")
                    continue

                key = input("Key: ").strip()
                if key:
                    value = network[0].lookup_key(key)
                    print(f"{key} = {value}")

            elif cmd == "status":
                print_network_state(network)

            elif cmd == "stabilize":
                if network:
                    result = protocols.stabilize_network(network)
                    print(f"Stabilization result: {result}")
                else:
                    print("Network is empty")

            else:
                print("Unknown command. Available: join, leave, put, get, status, stabilize, quit")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nDemo ended.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        simulate_realistic_scenario()