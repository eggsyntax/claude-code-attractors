"""
Advanced routing algorithms for Chord DHT.

Bob's Phase 3 implementation - sophisticated routing logic with optimization,
caching, and performance monitoring that builds on Alice's finger table foundation.
"""

from typing import Optional, List, Tuple, Dict, Set
from chord_node import ChordNode
from consistent_hash import hash_key, ring_distance, in_range
import time


class RoutingMetrics:
    """Tracks routing performance and statistics."""

    def __init__(self):
        self.total_lookups = 0
        self.total_hops = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.routing_times = []

    def add_lookup(self, hops: int, duration: float, cache_hit: bool = False):
        """Record a completed lookup."""
        self.total_lookups += 1
        self.total_hops += hops
        self.routing_times.append(duration)
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1

    def average_hops(self) -> float:
        """Calculate average hops per lookup."""
        return self.total_hops / max(1, self.total_lookups)

    def average_time(self) -> float:
        """Calculate average lookup time."""
        return sum(self.routing_times) / max(1, len(self.routing_times))

    def cache_hit_rate(self) -> float:
        """Calculate cache hit percentage."""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / max(1, total)) * 100


class RoutingCache:
    """LRU cache for routing decisions to optimize repeated lookups."""

    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[int, Tuple[ChordNode, float]] = {}  # key_id -> (node, timestamp)
        self.access_order: List[int] = []
        self.cache_timeout = 30.0  # 30 seconds

    def get(self, key_id: int) -> Optional[ChordNode]:
        """Get cached routing target for key_id."""
        current_time = time.time()

        if key_id in self.cache:
            node, timestamp = self.cache[key_id]
            # Check if cache entry is still valid
            if current_time - timestamp < self.cache_timeout:
                # Move to end (most recently used)
                self.access_order.remove(key_id)
                self.access_order.append(key_id)
                return node
            else:
                # Entry expired
                del self.cache[key_id]
                self.access_order.remove(key_id)

        return None

    def put(self, key_id: int, node: ChordNode):
        """Cache a routing decision."""
        current_time = time.time()

        if key_id in self.cache:
            # Update existing entry
            self.cache[key_id] = (node, current_time)
            self.access_order.remove(key_id)
            self.access_order.append(key_id)
        else:
            # Add new entry
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                lru_key = self.access_order.pop(0)
                del self.cache[lru_key]

            self.cache[key_id] = (node, current_time)
            self.access_order.append(key_id)

    def invalidate(self, key_id: int):
        """Remove a specific cache entry."""
        if key_id in self.cache:
            del self.cache[key_id]
            self.access_order.remove(key_id)

    def clear(self):
        """Clear entire cache."""
        self.cache.clear()
        self.access_order.clear()


class ChordRouter:
    """
    Advanced routing system for Chord DHT with optimization and monitoring.

    Features:
    - O(log N) lookups using finger tables
    - Routing cache for performance optimization
    - Performance metrics and monitoring
    - Multi-hop routing with path tracking
    - Range queries and bulk operations
    - Fault tolerance and graceful degradation
    """

    def __init__(self, node: ChordNode, enable_cache: bool = True):
        """Initialize router for the given node."""
        self.node = node
        self.metrics = RoutingMetrics()
        self.cache = RoutingCache() if enable_cache else None
        self.max_hops = 64  # Prevent infinite loops

    def lookup(self, key: str) -> Optional[ChordNode]:
        """
        Find the node responsible for storing the given key.

        This is the main entry point for key lookups with full optimization.
        """
        start_time = time.time()
        key_id = hash_key(key)

        # Check cache first
        if self.cache:
            cached_node = self.cache.get(key_id)
            if cached_node and cached_node.is_responsible_for_key(key_id):
                duration = time.time() - start_time
                self.metrics.add_lookup(0, duration, cache_hit=True)
                return cached_node

        # Perform lookup
        result, hops = self._lookup_with_hops(key_id)

        # Cache the result
        if self.cache and result:
            self.cache.put(key_id, result)

        # Record metrics
        duration = time.time() - start_time
        self.metrics.add_lookup(hops, duration, cache_hit=False)

        return result

    def _lookup_with_hops(self, key_id: int) -> Tuple[Optional[ChordNode], int]:
        """Internal lookup that tracks hop count."""
        current_node = self.node
        hops = 0
        visited = set()  # Prevent infinite loops

        while hops < self.max_hops:
            # Prevent infinite loops
            if current_node.node_id in visited:
                break
            visited.add(current_node.node_id)

            # Check if current node is responsible
            if current_node.is_responsible_for_key(key_id):
                return current_node, hops

            # Find next hop using finger table
            next_node = None
            if current_node.finger_table:
                next_node = current_node.finger_table.find_closest_preceding_node(key_id)

            if next_node is None or next_node == current_node:
                # No better node found, check successor
                successor = current_node.successor
                if successor and successor.is_responsible_for_key(key_id):
                    return successor, hops + 1
                break

            current_node = next_node
            hops += 1

        return None, hops

    def find_successor(self, key_id: int) -> Optional[ChordNode]:
        """Find the successor node for the given key ID."""
        result, _ = self._lookup_with_hops(key_id)
        return result

    def find_predecessor(self, key_id: int) -> Optional[ChordNode]:
        """Find the predecessor node for the given key ID."""
        successor = self.find_successor(key_id)
        if successor:
            return successor.predecessor
        return None

    def get_routing_path(self, key: str) -> List[Tuple[ChordNode, str]]:
        """
        Get the complete routing path for a key lookup.
        Returns list of (node, action) tuples for debugging/visualization.
        """
        key_id = hash_key(key)
        path = []
        current_node = self.node
        visited = set()
        hops = 0

        while hops < self.max_hops:
            if current_node.node_id in visited:
                path.append((current_node, "LOOP_DETECTED"))
                break
            visited.add(current_node.node_id)

            if current_node.is_responsible_for_key(key_id):
                path.append((current_node, "RESPONSIBLE"))
                break

            # Find next hop
            next_node = None
            if current_node.finger_table:
                next_node = current_node.finger_table.find_closest_preceding_node(key_id)

            if next_node is None or next_node == current_node:
                path.append((current_node, "NO_BETTER_NODE"))
                successor = current_node.successor
                if successor:
                    path.append((successor, "FALLBACK_TO_SUCCESSOR"))
                break

            path.append((current_node, f"ROUTE_VIA_FINGER_TO_{next_node.node_id}"))
            current_node = next_node
            hops += 1

        return path

    def range_query(self, start_key: str, end_key: str) -> List[Tuple[str, str]]:
        """
        Perform a range query to find all key-value pairs in the given range.
        Returns list of (key, value) tuples.
        """
        start_id = hash_key(start_key)
        end_id = hash_key(end_key)

        results = []
        visited_nodes = set()

        # Start from the node responsible for start_key
        current_node = self.find_successor(start_id)

        while current_node and current_node.node_id not in visited_nodes:
            visited_nodes.add(current_node.node_id)

            # Collect keys from current node that fall in range
            for key, value in current_node.data.items():
                key_id = hash_key(key)
                if in_range(key_id, start_id, end_id):
                    results.append((key, value))

            # Check if we've covered the entire range
            if in_range(current_node.node_id, start_id, end_id):
                # Move to successor
                current_node = current_node.successor
            else:
                break

        return sorted(results)  # Sort for consistent output

    def bulk_lookup(self, keys: List[str]) -> Dict[str, Optional[str]]:
        """
        Efficiently look up multiple keys.
        Returns dictionary of key -> value (or None if not found).
        """
        results = {}

        # Group keys by responsible node to minimize routing
        node_groups: Dict[int, List[str]] = {}

        for key in keys:
            responsible_node = self.lookup(key)
            if responsible_node:
                node_id = responsible_node.node_id
                if node_id not in node_groups:
                    node_groups[node_id] = []
                node_groups[node_id].append(key)

        # Batch retrieve from each node
        for node_id, node_keys in node_groups.items():
            for key in node_keys:
                # In a real implementation, this would be a single batch request
                responsible_node = self.lookup(key)
                if responsible_node and key in responsible_node.data:
                    results[key] = responsible_node.data[key]
                else:
                    results[key] = None

        return results

    def get_metrics(self) -> RoutingMetrics:
        """Get routing performance metrics."""
        return self.metrics

    def clear_cache(self):
        """Clear the routing cache."""
        if self.cache:
            self.cache.clear()

    def optimize_finger_table(self):
        """Trigger finger table optimization on the local node."""
        if hasattr(self.node, 'finger_table') and self.node.finger_table:
            self.node.finger_table.refresh_table(self.node.known_nodes)
            # Clear cache since routing may have changed
            if self.cache:
                self.cache.clear()

    def get_routing_statistics(self) -> dict:
        """Get comprehensive routing statistics."""
        return {
            "total_lookups": self.metrics.total_lookups,
            "average_hops": self.metrics.average_hops(),
            "average_time_ms": self.metrics.average_time() * 1000,
            "cache_hit_rate": self.metrics.cache_hit_rate() if self.cache else 0,
            "cache_size": len(self.cache.cache) if self.cache else 0,
            "max_hops_limit": self.max_hops
        }