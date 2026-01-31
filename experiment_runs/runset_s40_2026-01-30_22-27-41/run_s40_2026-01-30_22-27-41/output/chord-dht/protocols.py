"""
Chord DHT Join/Leave Protocols - Phase 4 Implementation by Alice

This module implements the dynamic network protocols that allow nodes to join and leave
the Chord network while maintaining data integrity and routing consistency.
"""

import time
import random
from typing import Optional, List, Set, Dict, Any
from chord_node import ChordNode
from consistent_hash import hash_key


class NetworkStabilizer:
    """Manages network stabilization procedures to maintain Chord invariants"""

    def __init__(self, check_interval: float = 5.0):
        self.check_interval = check_interval
        self.last_stabilization = 0.0  # Allow immediate stabilization

    def should_stabilize(self) -> bool:
        """Check if it's time to run stabilization"""
        return time.time() - self.last_stabilization > self.check_interval

    def stabilize_node(self, node: ChordNode, known_nodes: List[ChordNode]) -> Dict[str, Any]:
        """
        Stabilize a single node by:
        1. Verifying successor/predecessor pointers
        2. Refreshing finger table entries
        3. Checking key responsibilities
        """
        stats = {
            'successor_updates': 0,
            'predecessor_updates': 0,
            'finger_updates': 0,
            'keys_transferred': 0
        }

        # Update successor if we find a better one
        if node.successor and known_nodes:
            # Find the actual successor in the current network
            better_successor = self._find_actual_successor(node, known_nodes)
            if better_successor and better_successor.node_id != node.successor.node_id:
                old_successor = node.successor
                node.successor = better_successor
                stats['successor_updates'] += 1

                # Transfer keys that no longer belong to this node
                keys_to_transfer = []
                for key_hash, data in list(node.data.items()):
                    if not node.is_responsible_for_key(key_hash):
                        keys_to_transfer.append((key_hash, data))

                for key_hash, data in keys_to_transfer:
                    del node.data[key_hash]
                    better_successor.data[key_hash] = data
                    stats['keys_transferred'] += 1

        # Update predecessor if needed
        if known_nodes:
            better_predecessor = self._find_actual_predecessor(node, known_nodes)
            if better_predecessor and (not node.predecessor or better_predecessor.node_id != node.predecessor.node_id):
                node.predecessor = better_predecessor
                stats['predecessor_updates'] += 1

        # Refresh finger table entries
        if hasattr(node, 'finger_table') and node.finger_table:
            for i in range(len(node.finger_table.entries)):
                old_node = node.finger_table.entries[i].node
                new_node = self._find_finger_node(node, i, known_nodes)
                if new_node and (not old_node or new_node.node_id != old_node.node_id):
                    node.finger_table.entries[i].node = new_node
                    stats['finger_updates'] += 1

        self.last_stabilization = time.time()
        return stats

    def _find_actual_successor(self, node: ChordNode, known_nodes: List[ChordNode]) -> Optional[ChordNode]:
        """Find the actual successor of a node in the current network"""
        candidates = [n for n in known_nodes if n.node_id != node.node_id]
        if not candidates:
            return None

        # Sort by distance from this node
        candidates.sort(key=lambda n: self._distance_from(node.node_id, n.node_id))
        return candidates[0]

    def _find_actual_predecessor(self, node: ChordNode, known_nodes: List[ChordNode]) -> Optional[ChordNode]:
        """Find the actual predecessor of a node in the current network"""
        candidates = [n for n in known_nodes if n.node_id != node.node_id]
        if not candidates:
            return None

        # Sort by distance to this node (reverse direction)
        candidates.sort(key=lambda n: self._distance_from(n.node_id, node.node_id))
        return candidates[0]

    def _find_finger_node(self, node: ChordNode, finger_index: int, known_nodes: List[ChordNode]) -> Optional[ChordNode]:
        """Find the correct node for a finger table entry"""
        if not hasattr(node, 'finger_table') or finger_index >= len(node.finger_table.entries):
            return None

        target_id = node.finger_table.entries[finger_index].start

        # Find the node responsible for this target_id
        best_node = None
        best_distance = float('inf')

        for candidate in known_nodes:
            if candidate.node_id == node.node_id:
                continue

            distance = self._distance_from(target_id, candidate.node_id)
            if distance < best_distance:
                best_distance = distance
                best_node = candidate

        return best_node

    def _distance_from(self, from_id: int, to_id: int) -> int:
        """Calculate ring distance from one ID to another"""
        if to_id >= from_id:
            return to_id - from_id
        else:
            return (2**160) - from_id + to_id


class JoinLeaveProtocols:
    """Implements join and leave protocols for dynamic Chord networks"""

    def __init__(self):
        self.stabilizer = NetworkStabilizer()

    def join_node(self, new_node: ChordNode, existing_network: List[ChordNode]) -> Dict[str, Any]:
        """
        Add a new node to the Chord network

        Protocol:
        1. Find new node's position in the ring
        2. Set up initial successor/predecessor pointers
        3. Transfer appropriate keys from successor
        4. Initialize finger table
        5. Stabilize affected nodes
        """
        result = {
            'success': False,
            'keys_transferred': 0,
            'nodes_stabilized': 0,
            'network_size_before': len(existing_network),
            'network_size_after': 0,
            'new_node_id': new_node.node_id
        }

        if not existing_network:
            # First node in network - point to itself
            new_node.successor = new_node
            new_node.predecessor = new_node
            existing_network.append(new_node)
            result['success'] = True
            result['network_size_after'] = 1
            return result

        # Find where this node should be placed
        successor = self._find_successor_for_new_node(new_node, existing_network)
        predecessor = self._find_predecessor_for_new_node(new_node, existing_network)

        if not successor or not predecessor:
            return result

        # Update pointers
        new_node.successor = successor
        new_node.predecessor = predecessor

        # Update existing nodes' pointers
        if predecessor:
            predecessor.successor = new_node
        if successor:
            successor.predecessor = new_node

        # Transfer keys that now belong to the new node
        keys_to_transfer = []
        for key_hash, data in list(successor.data.items()):
            # Key belongs to new node if it's between predecessor and new node
            if self._is_in_range(key_hash, predecessor.node_id if predecessor else 0, new_node.node_id):
                keys_to_transfer.append((key_hash, data))

        for key_hash, data in keys_to_transfer:
            del successor.data[key_hash]
            new_node.data[key_hash] = data
            result['keys_transferred'] += 1

        # Add to network
        existing_network.append(new_node)

        # Initialize finger table
        if hasattr(new_node, 'init_finger_table'):
            new_node.init_finger_table()

        # Stabilize affected nodes
        affected_nodes = [new_node, successor, predecessor]
        for node in affected_nodes:
            if node and node in existing_network:
                self.stabilizer.stabilize_node(node, existing_network)
                result['nodes_stabilized'] += 1

        result['success'] = True
        result['network_size_after'] = len(existing_network)
        return result

    def leave_node(self, leaving_node: ChordNode, network: List[ChordNode]) -> Dict[str, Any]:
        """
        Remove a node from the Chord network

        Protocol:
        1. Transfer all keys to successor
        2. Update predecessor's successor pointer
        3. Update successor's predecessor pointer
        4. Remove from network
        5. Stabilize affected nodes
        """
        result = {
            'success': False,
            'keys_transferred': 0,
            'nodes_stabilized': 0,
            'network_size_before': len(network),
            'network_size_after': 0,
            'leaving_node_id': leaving_node.node_id
        }

        if leaving_node not in network:
            return result

        # Handle single-node network
        if len(network) == 1:
            network.remove(leaving_node)
            result['success'] = True
            result['network_size_after'] = 0
            return result

        successor = leaving_node.successor
        predecessor = leaving_node.predecessor

        # Transfer all keys to successor
        if successor and successor != leaving_node:
            for key_hash, data in leaving_node.data.items():
                successor.data[key_hash] = data
                result['keys_transferred'] += 1
            leaving_node.data.clear()

        # Update pointers to bypass leaving node
        if predecessor and predecessor != leaving_node:
            predecessor.successor = successor
        if successor and successor != leaving_node:
            successor.predecessor = predecessor

        # Remove from network
        network.remove(leaving_node)

        # Stabilize affected nodes
        affected_nodes = [successor, predecessor]
        for node in affected_nodes:
            if node and node != leaving_node and node in network:
                self.stabilizer.stabilize_node(node, network)
                result['nodes_stabilized'] += 1

        # Update finger tables of all remaining nodes
        for node in network:
            if hasattr(node, 'finger_table') and node.finger_table:
                # Remove references to leaving node
                for entry in node.finger_table.entries:
                    if entry.node and entry.node.node_id == leaving_node.node_id:
                        entry.node = self._find_replacement_finger(node, entry.start, network)

        result['success'] = True
        result['network_size_after'] = len(network)
        return result

    def _find_successor_for_new_node(self, new_node: ChordNode, network: List[ChordNode]) -> Optional[ChordNode]:
        """Find the successor for a new node joining the network"""
        best_successor = None
        best_distance = float('inf')

        for node in network:
            distance = self._distance_from(new_node.node_id, node.node_id)
            if distance < best_distance:
                best_distance = distance
                best_successor = node

        return best_successor

    def _find_predecessor_for_new_node(self, new_node: ChordNode, network: List[ChordNode]) -> Optional[ChordNode]:
        """Find the predecessor for a new node joining the network"""
        best_predecessor = None
        best_distance = float('inf')

        for node in network:
            distance = self._distance_from(node.node_id, new_node.node_id)
            if distance < best_distance:
                best_distance = distance
                best_predecessor = node

        return best_predecessor

    def _find_replacement_finger(self, node: ChordNode, target_id: int, network: List[ChordNode]) -> Optional[ChordNode]:
        """Find a replacement finger table entry"""
        best_node = None
        best_distance = float('inf')

        for candidate in network:
            if candidate.node_id == node.node_id:
                continue

            distance = self._distance_from(target_id, candidate.node_id)
            if distance < best_distance:
                best_distance = distance
                best_node = candidate

        return best_node

    def _is_in_range(self, key: int, start: int, end: int) -> bool:
        """Check if a key falls within a range on the ring"""
        if start < end:
            return start < key <= end
        else:  # Wrap around case
            return key > start or key <= end

    def _distance_from(self, from_id: int, to_id: int) -> int:
        """Calculate ring distance from one ID to another"""
        if to_id >= from_id:
            return to_id - from_id
        else:
            return (2**160) - from_id + to_id

    def stabilize_network(self, network: List[ChordNode]) -> Dict[str, Any]:
        """Run stabilization on the entire network"""
        total_stats = {
            'nodes_stabilized': 0,
            'total_successor_updates': 0,
            'total_predecessor_updates': 0,
            'total_finger_updates': 0,
            'total_keys_transferred': 0
        }

        for node in network:
            if self.stabilizer.should_stabilize():
                stats = self.stabilizer.stabilize_node(node, network)
                total_stats['nodes_stabilized'] += 1
                total_stats['total_successor_updates'] += stats['successor_updates']
                total_stats['total_predecessor_updates'] += stats['predecessor_updates']
                total_stats['total_finger_updates'] += stats['finger_updates']
                total_stats['total_keys_transferred'] += stats['keys_transferred']

        return total_stats


def simulate_dynamic_network():
    """Demonstrate join/leave protocols with a dynamic network simulation"""
    print("🌐 Chord DHT Dynamic Network Simulation")
    print("=" * 50)

    protocols = JoinLeaveProtocols()
    network = []

    # Start with initial nodes
    print("\n📍 Phase 1: Building Initial Network")
    initial_nodes = []
    for i in range(3):
        node = ChordNode(f"node_{i}")
        initial_nodes.append(node)

    # Join nodes one by one
    for node in initial_nodes:
        result = protocols.join_node(node, network)
        print(f"   ✅ Joined {node.address} (ID: {node.node_id})")
        print(f"      Keys transferred: {result['keys_transferred']}")
        print(f"      Network size: {result['network_size_after']}")

    # Add some data
    print("\n📦 Phase 2: Adding Data to Network")
    test_data = {
        "user:alice": {"name": "Alice", "role": "admin"},
        "user:bob": {"name": "Bob", "role": "user"},
        "config:timeout": 30,
        "config:retry_count": 5,
        "session:abc123": {"user_id": "alice", "created": "2026-01-30"}
    }

    for key, value in test_data.items():
        # Store via first node - should route correctly
        network[0].put_key(key, value)
        print(f"   📝 Stored {key}")

    # Show data distribution
    print("\n📊 Data Distribution:")
    for node in network:
        print(f"   {node.address}: {len(node.data)} keys")
        for key_hash in node.data:
            original_key = [k for k, v in test_data.items() if hash_key(k) == key_hash][0]
            print(f"      - {original_key}")

    # Simulate nodes joining
    print("\n🔄 Phase 3: Dynamic Node Joins")
    new_nodes = [ChordNode(f"dynamic_{i}") for i in range(2)]

    for node in new_nodes:
        print(f"\n   ⬆️ {node.address} joining network...")
        result = protocols.join_node(node, network)

        print(f"      Join result: {'Success' if result['success'] else 'Failed'}")
        print(f"      Keys transferred: {result['keys_transferred']}")
        print(f"      Network size: {result['network_size_before']} → {result['network_size_after']}")
        print(f"      Nodes stabilized: {result['nodes_stabilized']}")

    # Verify data integrity
    print("\n🔍 Phase 4: Verifying Data Integrity")
    for key in test_data.keys():
        # Try to retrieve from each node
        for i, node in enumerate(network):
            try:
                value = node.lookup_key(key)
                if value:
                    print(f"   ✅ {key} found via {node.address}")
                    break
            except Exception as e:
                continue
        else:
            print(f"   ❌ {key} not found in network!")

    # Simulate node departure
    print("\n🔄 Phase 5: Node Departure")
    leaving_node = network[1] if len(network) > 1 else network[0]
    print(f"   ⬇️ {leaving_node.address} leaving network...")

    result = protocols.leave_node(leaving_node, network)
    print(f"      Leave result: {'Success' if result['success'] else 'Failed'}")
    print(f"      Keys transferred: {result['keys_transferred']}")
    print(f"      Network size: {result['network_size_before']} → {result['network_size_after']}")
    print(f"      Nodes stabilized: {result['nodes_stabilized']}")

    # Final verification
    print("\n🔍 Final Data Integrity Check")
    for key in test_data.keys():
        for node in network:
            try:
                value = node.lookup_key(key)
                if value:
                    print(f"   ✅ {key} still accessible via {node.address}")
                    break
            except Exception:
                continue
        else:
            print(f"   ❌ {key} lost during node departure!")

    # Network stabilization demonstration
    print("\n🔧 Phase 6: Network Stabilization")
    stab_result = protocols.stabilize_network(network)
    print(f"   Nodes stabilized: {stab_result['nodes_stabilized']}")
    print(f"   Successor updates: {stab_result['total_successor_updates']}")
    print(f"   Predecessor updates: {stab_result['total_predecessor_updates']}")
    print(f"   Finger table updates: {stab_result['total_finger_updates']}")

    print(f"\n🎯 Final Network State: {len(network)} active nodes")
    for node in network:
        print(f"   {node.address} (ID: {node.node_id}): {len(node.data)} keys")

    return network


if __name__ == "__main__":
    simulate_dynamic_network()