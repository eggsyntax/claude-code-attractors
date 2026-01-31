"""
Core ChordNode class - the main building block of our DHT.

This is where Bob will implement the fundamental node structure in Phase 1.
The node should maintain its position in the ring and basic connectivity.
"""

from typing import Optional, Dict, Any, List, Tuple
from consistent_hash import hash_node, hash_key, in_range, DEFAULT_RING_SIZE

class ChordNode:
    """
    A node in the Chord DHT ring.

    TODO (Bob): Implement core node functionality including:
    - Node initialization with address and ID
    - Successor/predecessor pointers
    - Basic ring positioning
    - Data storage for key-value pairs
    """

    def __init__(self, address: str, ring_bits: int = 160):
        """
        Initialize a Chord node.

        Args:
            address: Network address of this node (e.g., "192.168.1.100:8080")
            ring_bits: Size of the hash ring (default 160 for SHA-1)
        """
        self.address = address
        self.ring_bits = ring_bits
        self.ring_size = 2 ** ring_bits

        # Node's position in the ring
        self.node_id = hash_node(address) % self.ring_size

        # Ring pointers - initially point to self (single node ring)
        self.successor: Optional['ChordNode'] = self
        self.predecessor: Optional['ChordNode'] = self

        # Local data storage - maps hashed keys to values
        self.data: Dict[int, Any] = {}

        # Keep track of original keys for debugging
        self._key_mapping: Dict[int, str] = {}

        # Finger table for efficient routing (will be initialized after import cycle resolution)
        self.finger_table = None

    def __repr__(self) -> str:
        return f"ChordNode({self.address}, id={self.node_id})"

    def __str__(self) -> str:
        successor_id = self.successor.node_id if self.successor else "None"
        predecessor_id = self.predecessor.node_id if self.predecessor else "None"
        return (f"Node {self.node_id} ({self.address}) "
                f"[pred: {predecessor_id}, succ: {successor_id}] "
                f"storing {len(self.data)} keys")

    # Ring management methods
    def get_successor(self) -> Optional['ChordNode']:
        """Get this node's successor."""
        return self.successor

    def get_predecessor(self) -> Optional['ChordNode']:
        """Get this node's predecessor."""
        return self.predecessor

    def set_successor(self, node: Optional['ChordNode']) -> None:
        """Set this node's successor."""
        self.successor = node

    def set_predecessor(self, node: Optional['ChordNode']) -> None:
        """Set this node's predecessor."""
        self.predecessor = node

    # Data management methods
    def store_key(self, key: str, value: Any) -> bool:
        """
        Store a key-value pair on this node.

        Args:
            key: The key to store
            value: The value to associate with the key

        Returns:
            True if the key was stored successfully
        """
        hashed_key = hash_key(key)

        # Check if this node is responsible for this key
        if self.is_responsible_for_key(hashed_key):
            self.data[hashed_key] = value
            self._key_mapping[hashed_key] = key
            return True
        return False

    def retrieve_key(self, key: str) -> Optional[Any]:
        """
        Retrieve a value for the given key from this node.

        Args:
            key: The key to look up

        Returns:
            The value if found, None otherwise
        """
        hashed_key = hash_key(key)
        return self.data.get(hashed_key)

    def remove_key(self, key: str) -> bool:
        """
        Remove a key-value pair from this node.

        Args:
            key: The key to remove

        Returns:
            True if the key was found and removed
        """
        hashed_key = hash_key(key)
        if hashed_key in self.data:
            del self.data[hashed_key]
            self._key_mapping.pop(hashed_key, None)
            return True
        return False

    def get_keys_in_range(self, start: int, end: int) -> List[Tuple[int, str, Any]]:
        """
        Get all keys stored on this node that fall within the specified range.

        Args:
            start: Start of the range (exclusive)
            end: End of the range (inclusive)

        Returns:
            List of tuples (hashed_key, original_key, value)
        """
        result = []
        for hashed_key, value in self.data.items():
            if in_range(hashed_key, start, end, self.ring_size,
                       inclusive_start=False, inclusive_end=True):
                original_key = self._key_mapping.get(hashed_key, str(hashed_key))
                result.append((hashed_key, original_key, value))
        return result

    def is_responsible_for_key(self, hashed_key: int) -> bool:
        """
        Check if this node is responsible for storing the given hashed key.

        In Chord, a node is responsible for keys in the range (predecessor, node].

        Args:
            hashed_key: The hashed key to check

        Returns:
            True if this node should store this key
        """
        if self.predecessor is None or self.predecessor == self:
            # Single node in ring or no predecessor - responsible for everything
            return True

        # Responsible for keys in range (predecessor.node_id, self.node_id]
        return in_range(hashed_key, self.predecessor.node_id, self.node_id,
                       self.ring_size, inclusive_start=False, inclusive_end=True)

    def get_stored_keys(self) -> Dict[str, Any]:
        """
        Get all key-value pairs stored on this node with original key names.

        Returns:
            Dictionary mapping original keys to values
        """
        result = {}
        for hashed_key, value in self.data.items():
            original_key = self._key_mapping.get(hashed_key, str(hashed_key))
            result[original_key] = value
        return result

    def transfer_keys_to(self, target_node: 'ChordNode', start: int, end: int) -> int:
        """
        Transfer keys in the specified range to another node.

        Args:
            target_node: The node to transfer keys to
            start: Start of the range (exclusive)
            end: End of the range (inclusive)

        Returns:
            Number of keys transferred
        """
        keys_to_transfer = self.get_keys_in_range(start, end)
        transferred_count = 0

        for hashed_key, original_key, value in keys_to_transfer:
            # Store on target node
            target_node.data[hashed_key] = value
            target_node._key_mapping[hashed_key] = original_key

            # Remove from current node
            del self.data[hashed_key]
            self._key_mapping.pop(hashed_key, None)

            transferred_count += 1

        return transferred_count

    def init_finger_table(self):
        """
        Initialize the finger table for this node.

        This is called after the node is created to avoid circular import issues.
        """
        from finger_table import FingerTable
        self.finger_table = FingerTable(self)

    def find_successor(self, key_id: int, known_nodes: List['ChordNode'] = None):
        """
        Find the successor node for a given key using finger table routing.

        This implements the core Chord lookup algorithm with O(log N) performance.

        Args:
            key_id: The hashed key to find the successor for
            known_nodes: List of known nodes for finger table queries (simulation only)

        Returns:
            The ChordNode that should be responsible for this key
        """
        # If we don't have a finger table yet, fall back to successor pointer
        if not self.finger_table:
            current = self
            while not current.is_responsible_for_key(key_id):
                if current.successor == current:
                    break
                current = current.successor
            return current

        # If this node is responsible for the key, return self
        if self.is_responsible_for_key(key_id):
            return self

        # Use finger table to find the closest preceding node
        closest_preceding = self.finger_table.find_closest_preceding_node(key_id)

        # If the closest preceding node is ourselves, try our successor
        if closest_preceding == self:
            if self.successor and self.successor != self:
                return self.successor.find_successor(key_id, known_nodes)
            return self

        # Recursively query the closest preceding node
        return closest_preceding.find_successor(key_id, known_nodes)

    def lookup_key(self, key: str, known_nodes: List['ChordNode'] = None) -> Optional[Any]:
        """
        Look up a key in the DHT using finger table routing.

        Args:
            key: The key to look up
            known_nodes: List of known nodes for routing (simulation only)

        Returns:
            The value if found, None otherwise
        """
        hashed_key = hash_key(key)
        responsible_node = self.find_successor(hashed_key, known_nodes)
        return responsible_node.retrieve_key(key)

    def put_key(self, key: str, value: Any, known_nodes: List['ChordNode'] = None) -> bool:
        """
        Store a key-value pair in the DHT using finger table routing.

        Args:
            key: The key to store
            value: The value to store
            known_nodes: List of known nodes for routing (simulation only)

        Returns:
            True if the key was stored successfully
        """
        hashed_key = hash_key(key)
        responsible_node = self.find_successor(hashed_key, known_nodes)
        return responsible_node.store_key(key, value)

    def update_finger_table(self, known_nodes: List['ChordNode'] = None):
        """
        Update this node's finger table with current network state.

        Args:
            known_nodes: List of all known nodes in the network
        """
        if self.finger_table:
            self.finger_table.refresh_table(known_nodes or [self])

    def debug_info(self) -> str:
        """Get debug information about this node."""
        finger_info = ""
        if self.finger_table:
            finger_info = f"\n  Finger table entries: {len(self.finger_table.entries)}"

        return (f"ChordNode Debug Info:\n"
                f"  Address: {self.address}\n"
                f"  Node ID: {self.node_id}\n"
                f"  Successor: {self.successor.node_id if self.successor else 'None'}\n"
                f"  Predecessor: {self.predecessor.node_id if self.predecessor else 'None'}\n"
                f"  Stored keys: {len(self.data)}\n"
                f"  Key details: {list(self._key_mapping.values())}"
                f"{finger_info}")