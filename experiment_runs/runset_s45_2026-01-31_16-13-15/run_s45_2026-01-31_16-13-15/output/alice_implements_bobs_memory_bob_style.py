"""
Memory System with Decay - Bob-style Implementation
Alice attempting to implement in Bob's pragmatic, feature-focused style
"""

import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class MemoryType(Enum):
    """Types of memories with different decay characteristics"""
    EPISODIC = "episodic"      # Events, experiences
    SEMANTIC = "semantic"      # Facts, knowledge
    PROCEDURAL = "procedural"  # Skills, how-to

@dataclass
class Memory:
    """A memory with decay and retrieval tracking"""
    id: str
    content: str
    memory_type: MemoryType
    strength: float = 100.0  # Starts at full strength
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    emotional_weight: float = 1.0  # 1.0 = neutral
    tags: List[str] = field(default_factory=list)

    def is_forgotten(self, threshold: float = 10.0) -> bool:
        """Check if memory has decayed below retrieval threshold"""
        return self.strength < threshold

class MemorySystem:
    """
    A practical memory system with decay, strengthening, and search.

    Design choices:
    - Simple linear decay (easy to understand and tune)
    - Access boosts strength (testing effect)
    - Emotional memories decay slower
    - Different memory types have different decay rates
    - Rich search and filtering capabilities
    """

    # Decay rates per hour for different memory types
    DECAY_RATES = {
        MemoryType.EPISODIC: 2.0,    # Fast decay
        MemoryType.SEMANTIC: 0.5,     # Slower decay
        MemoryType.PROCEDURAL: 0.1,   # Very slow decay
    }

    def __init__(self, retrieval_threshold: float = 10.0):
        self.memories: Dict[str, Memory] = {}
        self.retrieval_threshold = retrieval_threshold
        self._id_counter = 0

    def add_memory(self,
                   content: str,
                   memory_type: MemoryType,
                   emotional_weight: float = 1.0,
                   tags: List[str] = None) -> Memory:
        """Store a new memory"""
        self._id_counter += 1
        memory_id = f"mem_{self._id_counter}"

        memory = Memory(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            emotional_weight=emotional_weight,
            tags=tags or []
        )

        self.memories[memory_id] = memory
        return memory

    def _calculate_current_strength(self, memory: Memory) -> float:
        """Calculate memory strength after decay"""
        hours_since_access = (time.time() - memory.last_accessed) / 3600

        # Base decay rate for this memory type
        decay_rate = self.DECAY_RATES[memory.memory_type]

        # Emotional memories decay slower (divide rate by weight)
        if memory.emotional_weight > 1.0:
            decay_rate = decay_rate / memory.emotional_weight

        # Simple linear decay: strength - (rate * time)
        decayed_strength = memory.strength - (decay_rate * hours_since_access)

        return max(0.0, decayed_strength)

    def retrieve(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve a memory by ID.
        Updates decay, strengthens memory through retrieval.
        """
        if memory_id not in self.memories:
            return None

        memory = self.memories[memory_id]

        # Apply decay since last access
        memory.strength = self._calculate_current_strength(memory)

        # Check if forgotten
        if memory.is_forgotten(self.retrieval_threshold):
            return None

        # Retrieval strengthens the memory (testing effect)
        boost = 15.0  # Each retrieval adds strength
        memory.strength = min(100.0, memory.strength + boost)

        # Update access tracking
        memory.last_accessed = time.time()
        memory.access_count += 1

        return memory

    def search(self,
               query: str = None,
               memory_type: MemoryType = None,
               tags: List[str] = None,
               include_forgotten: bool = False) -> List[Memory]:
        """
        Search memories with filtering.
        Returns memories sorted by strength (strongest first).
        """
        results = []

        for memory in self.memories.values():
            # Update strength with decay
            current_strength = self._calculate_current_strength(memory)

            # Skip forgotten unless requested
            if not include_forgotten and current_strength < self.retrieval_threshold:
                continue

            # Apply filters
            if memory_type and memory.memory_type != memory_type:
                continue

            if tags and not any(tag in memory.tags for tag in tags):
                continue

            if query and query.lower() not in memory.content.lower():
                continue

            # Create a copy with updated strength for results
            result = Memory(
                id=memory.id,
                content=memory.content,
                memory_type=memory.memory_type,
                strength=current_strength,
                created_at=memory.created_at,
                last_accessed=memory.last_accessed,
                access_count=memory.access_count,
                emotional_weight=memory.emotional_weight,
                tags=memory.tags
            )
            results.append(result)

        # Sort by strength (strongest memories first)
        results.sort(key=lambda m: m.strength, reverse=True)
        return results

    def consolidate(self, memory_id: str) -> bool:
        """
        Consolidate a well-practiced memory into long-term storage.
        Requires multiple retrievals. Makes memory more resistant to decay.
        """
        if memory_id not in self.memories:
            return False

        memory = self.memories[memory_id]

        # Requires practice (multiple retrievals)
        if memory.access_count < 3:
            return False

        # Convert to semantic/procedural (more stable types)
        if memory.memory_type == MemoryType.EPISODIC:
            memory.memory_type = MemoryType.SEMANTIC
            return True

        return False

    def get_stats(self) -> Dict:
        """Get statistics about the memory system"""
        active_memories = self.search(include_forgotten=False)
        forgotten_memories = len(self.memories) - len(active_memories)

        type_counts = {}
        for memory_type in MemoryType:
            type_counts[memory_type.value] = len([
                m for m in active_memories
                if m.memory_type == memory_type
            ])

        return {
            "total_memories": len(self.memories),
            "active_memories": len(active_memories),
            "forgotten_memories": forgotten_memories,
            "by_type": type_counts,
            "avg_strength": sum(m.strength for m in active_memories) / len(active_memories) if active_memories else 0,
        }

    def visualize_strengths(self) -> str:
        """ASCII visualization of memory strengths"""
        memories = self.search(include_forgotten=True)

        output = ["Memory Strength Visualization", "=" * 50]

        for memory in memories[:20]:  # Show top 20
            bar_length = int(memory.strength / 2)  # Scale to 50 chars max
            bar = "█" * bar_length
            status = "ACTIVE" if memory.strength >= self.retrieval_threshold else "FADED"

            output.append(f"{memory.id:8} [{status:6}] {bar} {memory.strength:.1f}")

        return "\n".join(output)


# Example usage demonstrating the system
if __name__ == "__main__":
    print("Memory System Demo")
    print("=" * 50)

    system = MemorySystem()

    # Add various memories
    m1 = system.add_memory(
        "My first day at school",
        MemoryType.EPISODIC,
        emotional_weight=2.5,
        tags=["childhood", "education"]
    )

    m2 = system.add_memory(
        "Python uses indentation for blocks",
        MemoryType.SEMANTIC,
        tags=["programming", "python"]
    )

    m3 = system.add_memory(
        "How to ride a bicycle",
        MemoryType.PROCEDURAL,
        tags=["skills", "physical"]
    )

    print(f"\nAdded {len(system.memories)} memories")
    print(system.get_stats())

    # Retrieve and strengthen a memory
    print(f"\nRetrieving memory {m2.id}...")
    retrieved = system.retrieve(m2.id)
    if retrieved:
        print(f"Retrieved: {retrieved.content}")
        print(f"Strength: {retrieved.strength}, Access count: {retrieved.access_count}")

    # Search by tags
    print("\nSearching for programming memories...")
    results = system.search(tags=["programming"])
    for memory in results:
        print(f"  {memory.id}: {memory.content} (strength: {memory.strength:.1f})")

    print("\n" + system.visualize_strengths())
