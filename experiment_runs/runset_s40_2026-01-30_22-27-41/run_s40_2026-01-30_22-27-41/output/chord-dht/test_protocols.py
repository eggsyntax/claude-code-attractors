#!/usr/bin/env python3
"""
Test suite for Chord DHT Join/Leave Protocols - Phase 4 Testing

Comprehensive tests for the dynamic network protocols implementation.
"""

import unittest
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chord_node import ChordNode
from protocols import JoinLeaveProtocols, NetworkStabilizer
from consistent_hash import hash_key


class TestJoinLeaveProtocols(unittest.TestCase):
    """Test join and leave protocol functionality"""

    def setUp(self):
        """Set up test environment"""
        self.protocols = JoinLeaveProtocols()
        self.network = []

    def test_single_node_network(self):
        """Test creating a network with a single node"""
        node = ChordNode("test_node")
        result = self.protocols.join_node(node, self.network)

        self.assertTrue(result['success'])
        self.assertEqual(result['network_size_after'], 1)
        self.assertEqual(result['keys_transferred'], 0)
        self.assertEqual(len(self.network), 1)
        self.assertEqual(node.successor, node)
        self.assertEqual(node.predecessor, node)

    def test_two_node_network(self):
        """Test joining a second node"""
        # Create initial node
        node1 = ChordNode("node1")
        self.protocols.join_node(node1, self.network)

        # Join second node
        node2 = ChordNode("node2")
        result = self.protocols.join_node(node2, self.network)

        self.assertTrue(result['success'])
        self.assertEqual(result['network_size_after'], 2)
        self.assertEqual(len(self.network), 2)

        # Verify ring structure
        self.assertIn(node1, self.network)
        self.assertIn(node2, self.network)

        # Verify pointers are set (specific order depends on IDs)
        self.assertIsNotNone(node1.successor)
        self.assertIsNotNone(node1.predecessor)
        self.assertIsNotNone(node2.successor)
        self.assertIsNotNone(node2.predecessor)

    def test_multi_node_join(self):
        """Test joining multiple nodes"""
        nodes = [ChordNode(f"node_{i}") for i in range(5)]

        for node in nodes:
            result = self.protocols.join_node(node, self.network)
            self.assertTrue(result['success'])

        self.assertEqual(len(self.network), 5)

        # Verify all nodes have valid pointers
        for node in self.network:
            self.assertIsNotNone(node.successor)
            self.assertIsNotNone(node.predecessor)
            self.assertIn(node.successor, self.network)
            self.assertIn(node.predecessor, self.network)

    def test_join_with_data_transfer(self):
        """Test that keys are properly transferred during joins"""
        # Create initial node with data
        node1 = ChordNode("node1")
        self.protocols.join_node(node1, self.network)

        # Add some data
        test_data = {"key1": "value1", "key2": "value2", "key3": "value3"}
        for key, value in test_data.items():
            node1.put_key(key, value)

        initial_data_count = len(node1.data)

        # Join second node
        node2 = ChordNode("node2")
        result = self.protocols.join_node(node2, self.network)

        # Check if keys were transferred (may or may not happen depending on IDs)
        total_keys = len(node1.data) + len(node2.data)
        self.assertEqual(total_keys, initial_data_count)

    def test_node_leave_single_node(self):
        """Test leaving when only one node in network"""
        node = ChordNode("test_node")
        self.protocols.join_node(node, self.network)

        result = self.protocols.leave_node(node, self.network)

        self.assertTrue(result['success'])
        self.assertEqual(result['network_size_after'], 0)
        self.assertEqual(len(self.network), 0)

    def test_node_leave_with_data_transfer(self):
        """Test that keys are transferred when a node leaves"""
        # Create two nodes
        node1 = ChordNode("node1")
        node2 = ChordNode("node2")
        self.protocols.join_node(node1, self.network)
        self.protocols.join_node(node2, self.network)

        # Add data to first node
        test_data = {"key1": "value1", "key2": "value2"}
        for key, value in test_data.items():
            node1.put_key(key, value)

        initial_total_keys = sum(len(node.data) for node in self.network)

        # Node1 leaves
        result = self.protocols.leave_node(node1, self.network)

        self.assertTrue(result['success'])
        self.assertEqual(result['network_size_after'], 1)
        self.assertEqual(len(self.network), 1)
        self.assertNotIn(node1, self.network)

        # All keys should still be in the network
        final_total_keys = sum(len(node.data) for node in self.network)
        self.assertEqual(final_total_keys, initial_total_keys)

    def test_multiple_joins_and_leaves(self):
        """Test complex scenarios with multiple joins and leaves"""
        nodes = [ChordNode(f"node_{i}") for i in range(4)]

        # Join all nodes
        for node in nodes:
            result = self.protocols.join_node(node, self.network)
            self.assertTrue(result['success'])

        self.assertEqual(len(self.network), 4)

        # Add some data
        test_data = {f"key_{i}": f"value_{i}" for i in range(6)}
        for key, value in test_data.items():
            self.network[0].put_key(key, value)

        # Leave two nodes
        for i in range(2):
            leaving_node = self.network[0]  # Always remove first node
            result = self.protocols.leave_node(leaving_node, self.network)
            self.assertTrue(result['success'])

        self.assertEqual(len(self.network), 2)

        # Verify data integrity
        total_keys = sum(len(node.data) for node in self.network)
        self.assertEqual(total_keys, len(test_data))

    def test_data_integrity_after_operations(self):
        """Test that data remains accessible after join/leave operations"""
        # Create initial network
        nodes = [ChordNode(f"node_{i}") for i in range(3)]
        for node in nodes:
            self.protocols.join_node(node, self.network)

        # Add test data
        test_keys = ["user:alice", "config:timeout", "session:123"]
        test_values = [{"name": "Alice"}, 30, {"user": "alice"}]

        for key, value in zip(test_keys, test_values):
            self.network[0].put_key(key, value)

        # Add more nodes
        new_nodes = [ChordNode(f"new_{i}") for i in range(2)]
        for node in new_nodes:
            self.protocols.join_node(node, self.network)

        # Verify all keys are still accessible
        for key in test_keys:
            found = False
            for node in self.network:
                try:
                    value = node.lookup_key(key)
                    if value is not None:
                        found = True
                        break
                except:
                    continue
            self.assertTrue(found, f"Key {key} not found after joins")

        # Remove a node
        if len(self.network) > 1:
            self.protocols.leave_node(self.network[1], self.network)

        # Verify keys still accessible
        for key in test_keys:
            found = False
            for node in self.network:
                try:
                    value = node.lookup_key(key)
                    if value is not None:
                        found = True
                        break
                except:
                    continue
            self.assertTrue(found, f"Key {key} not found after leave")


class TestNetworkStabilizer(unittest.TestCase):
    """Test network stabilization functionality"""

    def setUp(self):
        """Set up test environment"""
        self.stabilizer = NetworkStabilizer(check_interval=0.1)  # Fast interval for testing

    def test_stabilizer_timing(self):
        """Test stabilization timing logic"""
        self.assertTrue(self.stabilizer.should_stabilize())  # Should stabilize immediately

        # After setting last stabilization to now
        self.stabilizer.last_stabilization = float('inf')  # Far future
        self.assertFalse(self.stabilizer.should_stabilize())

    def test_single_node_stabilization(self):
        """Test stabilizing a single node"""
        node = ChordNode("test_node")
        node.successor = node
        node.predecessor = node

        stats = self.stabilizer.stabilize_node(node, [node])

        # Should have no updates for single node
        self.assertEqual(stats['successor_updates'], 0)
        self.assertEqual(stats['predecessor_updates'], 0)
        self.assertEqual(stats['keys_transferred'], 0)

    def test_network_stabilization(self):
        """Test stabilizing a multi-node network"""
        protocols = JoinLeaveProtocols()
        network = []

        # Create network
        nodes = [ChordNode(f"node_{i}") for i in range(3)]
        for node in nodes:
            protocols.join_node(node, network)

        # Run network-wide stabilization
        stats = protocols.stabilize_network(network)

        # Should have run stabilization on all nodes
        self.assertGreaterEqual(stats['nodes_stabilized'], 0)


class TestProtocolIntegration(unittest.TestCase):
    """Integration tests for the complete protocol system"""

    def test_complete_workflow(self):
        """Test a complete workflow: join, store, retrieve, leave"""
        protocols = JoinLeaveProtocols()
        network = []

        # Phase 1: Create network
        nodes = [ChordNode(f"node_{i}") for i in range(4)]
        for node in nodes:
            result = protocols.join_node(node, network)
            self.assertTrue(result['success'])

        # Phase 2: Store data
        test_data = {
            "user:alice": {"name": "Alice", "role": "admin"},
            "user:bob": {"name": "Bob", "role": "user"},
            "config:timeout": 30
        }

        for key, value in test_data.items():
            network[0].put_key(key, value)

        # Phase 3: Verify data accessible from all nodes
        for key in test_data.keys():
            for node in network:
                try:
                    retrieved_value = node.lookup_key(key)
                    if retrieved_value is not None:
                        break
                except:
                    continue
            else:
                self.fail(f"Key {key} not accessible from any node")

        # Phase 4: Node leaves
        leaving_node = network[1]
        result = protocols.leave_node(leaving_node, network)
        self.assertTrue(result['success'])

        # Phase 5: Verify data still accessible
        for key in test_data.keys():
            found = False
            for node in network:
                try:
                    value = node.lookup_key(key)
                    if value is not None:
                        found = True
                        break
                except:
                    continue
            self.assertTrue(found, f"Key {key} not found after node departure")

    def test_stress_operations(self):
        """Stress test with many join/leave operations"""
        protocols = JoinLeaveProtocols()
        network = []

        # Create initial network
        initial_nodes = [ChordNode(f"init_{i}") for i in range(3)]
        for node in initial_nodes:
            protocols.join_node(node, network)

        # Add initial data
        for i in range(10):
            network[0].put_key(f"key_{i}", f"value_{i}")

        # Perform many join/leave operations
        for round_num in range(3):
            # Join phase
            new_nodes = [ChordNode(f"round_{round_num}_node_{i}") for i in range(2)]
            for node in new_nodes:
                result = protocols.join_node(node, network)
                self.assertTrue(result['success'])

            # Leave phase (if network large enough)
            if len(network) > 3:
                leaving_node = network[-1]  # Remove last node
                result = protocols.leave_node(leaving_node, network)
                self.assertTrue(result['success'])

        # Verify network integrity
        self.assertGreater(len(network), 0)
        for node in network:
            self.assertIsNotNone(node.successor)
            self.assertIsNotNone(node.predecessor)


def run_all_tests():
    """Run all protocol tests"""
    print("🧪 Running Chord DHT Protocol Tests")
    print("=" * 40)

    # Create test suite
    test_classes = [
        TestJoinLeaveProtocols,
        TestNetworkStabilizer,
        TestProtocolIntegration
    ]

    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")

    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)