"""
Consistent hashing utilities for Chord DHT.

This module will be implemented by Bob in Phase 1.
It should include:
- Hash function (SHA-1)
- Node ID generation
- Key-to-hash conversion
- Ring distance calculations
"""

import hashlib
from typing import Union

# Ring configuration
DEFAULT_RING_BITS = 160
DEFAULT_RING_SIZE = 2 ** DEFAULT_RING_BITS

def hash_key(key: str) -> int:
    """
    Hash a data key using SHA-1.

    Args:
        key: The data key to hash

    Returns:
        Integer hash value in the range [0, 2^160)
    """
    return int(hashlib.sha1(key.encode('utf-8')).hexdigest(), 16)

def hash_node(node_address: str) -> int:
    """
    Hash a node address using SHA-1 to determine its position in the ring.

    Args:
        node_address: Network address of the node (e.g., "192.168.1.100:8080")

    Returns:
        Integer hash value representing the node's position in the ring
    """
    return int(hashlib.sha1(node_address.encode('utf-8')).hexdigest(), 16)

def ring_distance(start: int, end: int, ring_size: int = DEFAULT_RING_SIZE) -> int:
    """
    Calculate the clockwise distance between two points on the ring.

    Args:
        start: Starting position on the ring
        end: Ending position on the ring
        ring_size: Size of the ring (default 2^160)

    Returns:
        The clockwise distance from start to end
    """
    if end >= start:
        return end - start
    else:
        return (ring_size - start) + end

def in_range(key: int, start: int, end: int, ring_size: int = DEFAULT_RING_SIZE,
             inclusive_start: bool = False, inclusive_end: bool = True) -> bool:
    """
    Check if a key falls within a range on the ring.

    Args:
        key: The key to check
        start: Start of the range
        end: End of the range
        ring_size: Size of the ring
        inclusive_start: Whether to include the start point
        inclusive_end: Whether to include the end point

    Returns:
        True if the key is in the specified range
    """
    if start == end:
        # Special case: if start == end, the range covers the entire ring
        # unless we're looking for exact matches
        if inclusive_start and inclusive_end:
            return True
        else:
            return key == start if inclusive_start else False

    if start < end:
        # Normal case: range doesn't wrap around
        if inclusive_start and inclusive_end:
            return start <= key <= end
        elif inclusive_start:
            return start <= key < end
        elif inclusive_end:
            return start < key <= end
        else:
            return start < key < end
    else:
        # Range wraps around the ring
        if inclusive_start and inclusive_end:
            return (key >= start) or (key <= end)
        elif inclusive_start:
            return (key >= start) or (key < end)
        elif inclusive_end:
            return (key > start) or (key <= end)
        else:
            return (key > start) or (key < end)

def normalize_id(node_id: int, ring_size: int = DEFAULT_RING_SIZE) -> int:
    """
    Normalize a node ID to ensure it fits within the ring.

    Args:
        node_id: The node ID to normalize
        ring_size: Size of the ring

    Returns:
        Normalized node ID
    """
    return node_id % ring_size

# Legacy compatibility - keeping the old function name
def placeholder_hash(value: str) -> int:
    """Legacy compatibility function."""
    return hash_key(value)