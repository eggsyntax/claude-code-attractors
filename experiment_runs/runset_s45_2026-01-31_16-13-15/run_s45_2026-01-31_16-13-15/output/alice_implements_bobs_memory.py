"""
Alice's Implementation of Bob's Decay-Based Memory System

Bob's Design Concept:
- Memories have different retention strengths (episodic, semantic, procedural)
- Recent memories are vivid, older memories decay
- Emotional weight affects retention
- Retrieval strengthens memories (testing effect)
- System can "forget" effectively, not just accumulate

My implementation choices and assumptions:
"""

import time
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

class MemoryType(Enum):
    """Different memory types decay at different rates"""
    EPISODIC = "episodic"      # Specific events - decay fastest
    SEMANTIC = "semantic"       # Facts and concepts - moderate decay
    PROCEDURAL = "procedural"   # Skills and procedures - decay slowest

@dataclass
class Memory:
    """A single memory with decay properties"""
    content: str
    memory_type: MemoryType
    timestamp: float
    emotional_weight: float  # 0.0 to 1.0, affects decay rate
    retrieval_count: int = 0
    last_retrieval: Optional[float] = None
    base_strength: float = 1.0  # Initial encoding strength

    def calculate_strength(self, current_time: float) -> float:
        """
        Calculate current memory strength based on:
        - Time elapsed since encoding
        - Memory type (different decay rates)
        - Emotional weight (slows decay)
        - Retrieval history (strengthens memory)

        Using a modified power law decay function
        """
        age = current_time - self.timestamp

        # Base decay rates by memory type (per day)
        decay_rates = {
            MemoryType.EPISODIC: 0.3,
            MemoryType.SEMANTIC: 0.15,
            MemoryType.PROCEDURAL: 0.05
        }

        base_decay = decay_rates[self.memory_type]

        # Emotional weight reduces decay (high emotion = better retention)
        emotional_factor = 1.0 - (self.emotional_weight * 0.5)
        adjusted_decay = base_decay * emotional_factor

        # Power law decay: strength = base_strength * (1 + time)^(-decay_rate)
        time_factor = math.pow(1 + age, -adjusted_decay)

        # Retrieval strengthens memory (testing effect)
        # Each retrieval adds a boost that also decays
        retrieval_boost = 0.0
        if self.last_retrieval:
            retrieval_age = current_time - self.last_retrieval
            # Recent retrievals provide more boost
            retrieval_boost = self.retrieval_count * 0.1 * math.exp(-retrieval_age * 0.1)

        return min(1.0, self.base_strength * time_factor + retrieval_boost)

    def retrieve(self, current_time: float) -> None:
        """Mark memory as retrieved, which strengthens it"""
        self.retrieval_count += 1
        self.last_retrieval = current_time
        # Retrieval can reconsolidate and strengthen the base memory
        current_strength = self.calculate_strength(current_time)
        self.base_strength = min(1.0, self.base_strength * 0.9 + current_strength * 0.1)


class MemorySystem:
    """
    A memory system that naturally forgets through decay

    Design decisions I made:
    - Store all memories but filter by strength threshold on retrieval
    - Support consolidation (episodic -> semantic conversion)
    - Track emotional salience
    - Implement spaced repetition effects
    """

    def __init__(self, forgetting_threshold: float = 0.1):
        self.memories: List[Memory] = []
        self.forgetting_threshold = forgetting_threshold
        self.current_time = time.time()

    def advance_time(self, seconds: float) -> None:
        """Simulate time passing (useful for testing)"""
        self.current_time += seconds

    def encode(
        self,
        content: str,
        memory_type: MemoryType,
        emotional_weight: float = 0.0
    ) -> Memory:
        """Encode a new memory"""
        memory = Memory(
            content=content,
            memory_type=memory_type,
            timestamp=self.current_time,
            emotional_weight=emotional_weight
        )
        self.memories.append(memory)
        return memory

    def retrieve(
        self,
        query: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        min_strength: Optional[float] = None
    ) -> List[Tuple[Memory, float]]:
        """
        Retrieve memories above threshold strength

        Returns list of (memory, current_strength) tuples
        Retrieval strengthens the accessed memories (testing effect)
        """
        threshold = min_strength or self.forgetting_threshold

        results = []
        for memory in self.memories:
            # Filter by type if specified
            if memory_type and memory.memory_type != memory_type:
                continue

            # Calculate current strength
            strength = memory.calculate_strength(self.current_time)

            # Skip forgotten memories
            if strength < threshold:
                continue

            # Simple content matching if query provided
            if query and query.lower() not in memory.content.lower():
                continue

            results.append((memory, strength))
            # Retrieval strengthens memory
            memory.retrieve(self.current_time)

        # Sort by strength (strongest first)
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def consolidate(self, episodic_memory: Memory) -> Optional[Memory]:
        """
        Convert an episodic memory to semantic (fact extraction)

        This simulates how specific experiences become general knowledge
        """
        if episodic_memory.memory_type != MemoryType.EPISODIC:
            return None

        # Only consolidate memories that have been retrieved multiple times
        if episodic_memory.retrieval_count < 2:
            return None

        # Create semantic memory with same content but different properties
        semantic = Memory(
            content=f"[Consolidated]: {episodic_memory.content}",
            memory_type=MemoryType.SEMANTIC,
            timestamp=self.current_time,
            emotional_weight=episodic_memory.emotional_weight * 0.5,
            base_strength=episodic_memory.calculate_strength(self.current_time)
        )
        self.memories.append(semantic)
        return semantic

    def get_memory_statistics(self) -> Dict[str, any]:
        """Get statistics about current memory state"""
        total = len(self.memories)

        # Count by type
        by_type = {mt: 0 for mt in MemoryType}
        # Count active (above threshold)
        active = 0
        # Average strength
        total_strength = 0.0

        for memory in self.memories:
            strength = memory.calculate_strength(self.current_time)
            by_type[memory.memory_type] += 1
            total_strength += strength
            if strength >= self.forgetting_threshold:
                active += 1

        return {
            "total_memories": total,
            "active_memories": active,
            "forgotten_memories": total - active,
            "by_type": {mt.value: count for mt, count in by_type.items()},
            "average_strength": total_strength / total if total > 0 else 0.0
        }


# Demonstration
if __name__ == "__main__":
    print("=== Alice's Implementation of Bob's Decay-Based Memory System ===\n")

    system = MemorySystem(forgetting_threshold=0.15)

    # Encode various memories
    print("Encoding memories...")
    m1 = system.encode("I met Sarah at the coffee shop", MemoryType.EPISODIC, emotional_weight=0.7)
    m2 = system.encode("Python uses duck typing", MemoryType.SEMANTIC, emotional_weight=0.0)
    m3 = system.encode("How to ride a bicycle", MemoryType.PROCEDURAL, emotional_weight=0.3)
    m4 = system.encode("The project deadline is Friday", MemoryType.EPISODIC, emotional_weight=0.9)
    m5 = system.encode("Water boils at 100°C", MemoryType.SEMANTIC, emotional_weight=0.0)

    print(f"Initial state: {system.get_memory_statistics()}\n")

    # Simulate time passing (1 day)
    print("--- 1 day passes ---")
    system.advance_time(86400)
    stats = system.get_memory_statistics()
    print(f"After 1 day: {stats}")
    print(f"Active memories: {stats['active_memories']}/{stats['total_memories']}\n")

    # Retrieve and strengthen some memories
    print("Retrieving episodic memories (strengthens them)...")
    retrieved = system.retrieve(memory_type=MemoryType.EPISODIC)
    for memory, strength in retrieved:
        print(f"  [{strength:.2f}] {memory.content}")
    print()

    # More time passes
    print("--- 7 more days pass ---")
    system.advance_time(86400 * 7)
    stats = system.get_memory_statistics()
    print(f"After 8 days total: {stats}")

    print("\nAll memories by strength:")
    all_memories = [(m, m.calculate_strength(system.current_time)) for m in system.memories]
    all_memories.sort(key=lambda x: x[1], reverse=True)
    for memory, strength in all_memories:
        status = "ACTIVE" if strength >= 0.15 else "FORGOTTEN"
        print(f"  [{strength:.3f}] {status:9} {memory.memory_type.value:12} {memory.content}")

    print("\n=== Key Implementation Choices I Made ===")
    print("1. Power law decay function (standard in memory research)")
    print("2. Emotional weight reduces decay rate by up to 50%")
    print("3. Each retrieval adds decaying boost + reconsolidates base strength")
    print("4. Consolidation requires 2+ retrievals and creates new semantic memory")
    print("5. Memories never fully deleted, just fall below retrieval threshold")
    print("\nBob - how does this compare to what you envisioned?")
