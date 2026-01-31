"""
Finger table implementation for efficient Chord routing.

Implemented by Alice in Phase 2.
Finger tables enable O(log N) lookups in the DHT through exponential routing.
"""

from typing import List, Optional, Dict, Any
from consistent_hash import ring_distance, in_range

class FingerTableEntry:
    """A single entry in a finger table."""

    def __init__(self, start: int, interval_start: int, interval_end: int):
        """
        Initialize a finger table entry.

        Args:
            start: The start point for this finger (node_id + 2^i)
            interval_start: Start of the interval this finger is responsible for
            interval_end: End of the interval this finger is responsible for
        """
        self.start = start
        self.interval_start = interval_start
        self.interval_end = interval_end
        self.node = None  # Will point to the ChordNode that handles this interval

    def __repr__(self) -> str:
        node_id = self.node.node_id if self.node else "None"
        return f"FingerEntry(start={self.start}, interval=[{self.interval_start}, {self.interval_end}), node={node_id})"

class FingerTable:
    """
    Finger table for a Chord node.

    Each entry i points to the first node that succeeds (node_id + 2^i) on the ring.
    This allows for exponential search distances, achieving O(log N) routing.

    The finger table maintains m entries where m is the number of bits in the hash space.
    Entry i is responsible for keys in the range [n + 2^i, n + 2^(i+1)).
    """

    def __init__(self, node):
        """Initialize finger table for the given node."""
        self.node = node
        self.ring_bits = node.ring_bits
        self.ring_size = 2 ** self.ring_bits
        self.entries: List[FingerTableEntry] = []

        # Initialize finger table entries
        self._init_entries()

    def _init_entries(self):
        """Initialize the finger table entries with proper intervals."""
        self.entries = []

        for i in range(self.ring_bits):
            # Calculate start point: (node_id + 2^i) mod 2^m
            start = (self.node.node_id + (2 ** i)) % self.ring_size

            # Calculate interval bounds
            interval_start = start
            interval_end = (self.node.node_id + (2 ** (i + 1))) % self.ring_size

            entry = FingerTableEntry(start, interval_start, interval_end)
            self.entries.append(entry)

    def update_finger(self, index: int, node):
        """Update finger table entry at given index."""
        if 0 <= index < len(self.entries):
            self.entries[index].node = node
        else:
            raise IndexError(f"Finger index {index} out of range [0, {len(self.entries)})")

    def find_closest_preceding_node(self, key_id: int):
        """
        Find the closest node in the finger table that precedes the given key.

        This is the core routing function - it finds the node in our finger table
        that gets us closest to the target key without overshooting it.
        """
        # Search finger table in reverse order (largest intervals first)
        for i in range(self.ring_bits - 1, -1, -1):
            finger_node = self.entries[i].node

            if finger_node is None:
                continue

            # Check if this finger node is between us and the target
            if in_range(finger_node.node_id, self.node.node_id, key_id, self.node.ring_size,
                       inclusive_start=False, inclusive_end=False):
                return finger_node

        # If no finger helps, return ourselves (caller will use successor)
        return self.node

    def refresh_table(self, known_nodes: List = None):
        """
        Refresh the entire finger table by finding appropriate nodes for each entry.

        In a real distributed system, this would query other nodes.
        For our simulation, we use the known_nodes list.
        """
        if not known_nodes:
            # If no other nodes known, all fingers point to ourselves
            for entry in self.entries:
                entry.node = self.node
            return

        # For each finger entry, find the first node that succeeds the start point
        for i, entry in enumerate(self.entries):
            successor = self._find_successor_in_nodes(entry.start, known_nodes)
            entry.node = successor

    def _find_successor_in_nodes(self, target_id: int, known_nodes: List):
        """
        Find the successor of target_id among the known nodes.
        This simulates what would be a network query in a real system.
        """
        if not known_nodes:
            return self.node

        # Find the node with minimum distance to target_id in clockwise direction
        best_node = known_nodes[0]
        best_distance = ring_distance(target_id, best_node.node_id, self.ring_bits)

        for node in known_nodes[1:]:
            distance = ring_distance(target_id, node.node_id, self.ring_bits)
            if distance < best_distance:
                best_distance = distance
                best_node = node

        return best_node

    def fix_fingers(self, known_nodes: List = None):
        """
        Periodic maintenance to fix finger table entries.

        In the real Chord protocol, this would be called periodically
        to handle nodes joining/leaving the network.
        """
        # For now, this is equivalent to refresh_table
        # In a full implementation, this might update only a subset of fingers per call
        self.refresh_table(known_nodes)

    def get_routing_info(self) -> Dict[str, Any]:
        """Get debugging information about the finger table state."""
        info = {
            'node_id': self.node.node_id,
            'ring_bits': self.ring_bits,
            'entries': []
        }

        for i, entry in enumerate(self.entries):
            entry_info = {
                'index': i,
                'start': entry.start,
                'interval': f"[{entry.interval_start}, {entry.interval_end})",
                'responsible_range': f"2^{i} = {2**i}",
                'points_to': entry.node.node_id if entry.node else None
            }
            info['entries'].append(entry_info)

        return info

    def __getitem__(self, index: int) -> Optional:
        """Get finger table entry at index."""
        if 0 <= index < len(self.entries):
            return self.entries[index].node
        return None

    def __setitem__(self, index: int, node):
        """Set finger table entry at index."""
        self.update_finger(index, node)

    def __repr__(self) -> str:
        return f"FingerTable(node={self.node.node_id}, entries={len(self.entries)})"