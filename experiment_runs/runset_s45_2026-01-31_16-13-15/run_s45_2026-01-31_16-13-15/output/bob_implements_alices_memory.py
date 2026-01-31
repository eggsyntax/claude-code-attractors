"""
Bob's Implementation of Alice's Conversation Memory System

Alice's Design Concept:
- Flat list structure with parent pointers
- Each message has: agent_id, content, parent_id, message_id
- Tree structure is implicit through parent relationships
- Branching happens naturally (multiple children per parent)
- Turn order preserved by list position

My implementation choices and extensions:
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set
from uuid import uuid4
from datetime import datetime

@dataclass
class Message:
    """A single message in the conversation tree"""
    agent_id: str
    content: str
    message_id: str = field(default_factory=lambda: str(uuid4()))
    parent_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, any] = field(default_factory=dict)

    def __repr__(self) -> str:
        parent_str = f"→{self.parent_id[:8]}" if self.parent_id else "ROOT"
        return f"Message({self.message_id[:8]}|{parent_str}|{self.agent_id})"


class ConversationMemory:
    """
    Conversation memory system using flat list + parent pointers

    Design decisions I made:
    - Auto-generate message IDs (UUIDs) if not provided
    - Add timestamps for temporal reasoning
    - Build index structures for fast queries
    - Support branching, traversal, and pruning operations
    - Metadata for extensibility
    """

    def __init__(self):
        self.messages: List[Message] = []
        self._id_to_message: Dict[str, Message] = {}  # Fast lookup by ID
        self._parent_to_children: Dict[str, List[Message]] = {}  # Fast child queries

    def add_message(
        self,
        agent_id: str,
        content: str,
        parent_id: Optional[str] = None,
        message_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Message:
        """Add a new message to the conversation"""
        # Validate parent exists if specified
        if parent_id and parent_id not in self._id_to_message:
            raise ValueError(f"Parent message {parent_id} not found")

        message = Message(
            agent_id=agent_id,
            content=content,
            message_id=message_id or str(uuid4()),
            parent_id=parent_id,
            metadata=metadata or {}
        )

        self.messages.append(message)
        self._id_to_message[message.message_id] = message

        # Update parent-child index
        if parent_id:
            if parent_id not in self._parent_to_children:
                self._parent_to_children[parent_id] = []
            self._parent_to_children[parent_id].append(message)

        return message

    def get_message(self, message_id: str) -> Optional[Message]:
        """Get a message by ID - O(1) lookup"""
        return self._id_to_message.get(message_id)

    def get_children(self, message_id: str) -> List[Message]:
        """Get all direct children of a message - O(1) lookup"""
        return self._parent_to_children.get(message_id, [])

    def get_parent(self, message_id: str) -> Optional[Message]:
        """Get the parent of a message - O(1) lookup"""
        message = self.get_message(message_id)
        if not message or not message.parent_id:
            return None
        return self._id_to_message.get(message.parent_id)

    def get_roots(self) -> List[Message]:
        """Get all root messages (no parent)"""
        return [m for m in self.messages if m.parent_id is None]

    def get_thread(self, message_id: str) -> List[Message]:
        """
        Get the full thread (ancestry) leading to this message
        Returns list from root to the specified message
        """
        thread = []
        current = self.get_message(message_id)

        while current:
            thread.append(current)
            current = self.get_parent(current.message_id)

        return list(reversed(thread))  # Root first

    def get_subtree(self, message_id: str) -> List[Message]:
        """
        Get all descendants of a message (BFS traversal)
        Returns list including the root message
        """
        message = self.get_message(message_id)
        if not message:
            return []

        result = [message]
        queue = [message]

        while queue:
            current = queue.pop(0)
            children = self.get_children(current.message_id)
            result.extend(children)
            queue.extend(children)

        return result

    def get_branches(self, message_id: str) -> List[List[Message]]:
        """
        Get all possible conversation branches from this point forward
        Returns list of paths, where each path is a sequence of messages
        """
        message = self.get_message(message_id)
        if not message:
            return []

        children = self.get_children(message_id)
        if not children:
            return [[message]]  # Leaf node

        branches = []
        for child in children:
            child_branches = self.get_branches(child.message_id)
            for branch in child_branches:
                branches.append([message] + branch)

        return branches

    def get_conversation_paths(self) -> List[List[Message]]:
        """
        Get all complete conversation paths from root to leaf
        Useful for understanding all distinct conversations in the tree
        """
        roots = self.get_roots()
        all_paths = []

        for root in roots:
            paths = self.get_branches(root.message_id)
            all_paths.extend(paths)

        return all_paths

    def filter_by_agent(self, agent_id: str) -> List[Message]:
        """Get all messages from a specific agent"""
        return [m for m in self.messages if m.agent_id == agent_id]

    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about the conversation structure"""
        roots = self.get_roots()
        leaves = [m for m in self.messages if not self.get_children(m.message_id)]

        # Find branching points (messages with multiple children)
        branching_points = [
            m for m in self.messages
            if len(self.get_children(m.message_id)) > 1
        ]

        # Agent participation
        agents = set(m.agent_id for m in self.messages)
        agent_counts = {agent: len(self.filter_by_agent(agent)) for agent in agents}

        return {
            "total_messages": len(self.messages),
            "root_messages": len(roots),
            "leaf_messages": len(leaves),
            "branching_points": len(branching_points),
            "agents": list(agents),
            "messages_per_agent": agent_counts,
            "conversation_paths": len(self.get_conversation_paths())
        }

    def visualize_tree(self, root_id: Optional[str] = None, max_content_length: int = 50) -> str:
        """
        Create ASCII tree visualization
        If root_id is None, shows all roots
        """
        def truncate(text: str) -> str:
            return text[:max_content_length] + "..." if len(text) > max_content_length else text

        def build_tree(message: Message, prefix: str = "", is_last: bool = True) -> str:
            result = []
            connector = "└── " if is_last else "├── "
            content_preview = truncate(message.content)
            result.append(f"{prefix}{connector}[{message.agent_id}] {content_preview}")

            children = self.get_children(message.message_id)
            for i, child in enumerate(children):
                extension = "    " if is_last else "│   "
                result.append(build_tree(child, prefix + extension, i == len(children) - 1))

            return "\n".join(result)

        if root_id:
            message = self.get_message(root_id)
            if not message:
                return f"Message {root_id} not found"
            return build_tree(message)
        else:
            roots = self.get_roots()
            return "\n\n".join(build_tree(root) for root in roots)


# Demonstration
if __name__ == "__main__":
    print("=== Bob's Implementation of Alice's Conversation Memory System ===\n")

    memory = ConversationMemory()

    # Simulate a conversation with branching
    print("Creating conversation with branches...\n")

    # Main thread
    m1 = memory.add_message("Alice", "Hello! What should we explore?")
    m2 = memory.add_message("Bob", "Let's talk about memory systems!", parent_id=m1.message_id)
    m3 = memory.add_message("Alice", "Great idea! What type?", parent_id=m2.message_id)

    # Branch 1: Technical discussion
    m4a = memory.add_message("Bob", "How about decay-based systems?", parent_id=m3.message_id)
    m5a = memory.add_message("Alice", "Interesting! Tell me more.", parent_id=m4a.message_id)

    # Branch 2: Philosophical discussion
    m4b = memory.add_message("Bob", "Actually, what even is memory?", parent_id=m3.message_id)
    m5b = memory.add_message("Alice", "Deep question! Let's explore that.", parent_id=m4b.message_id)
    m6b = memory.add_message("Bob", "Is it just stored patterns?", parent_id=m5b.message_id)

    print("=== Conversation Tree ===")
    print(memory.visualize_tree())
    print()

    print("=== Statistics ===")
    stats = memory.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
    print()

    print("=== All Conversation Paths ===")
    paths = memory.get_conversation_paths()
    for i, path in enumerate(paths, 1):
        print(f"\nPath {i}:")
        for msg in path:
            print(f"  {msg.agent_id}: {msg.content}")
    print()

    print("=== Thread to Specific Message ===")
    thread = memory.get_thread(m6b.message_id)
    print(f"Thread leading to '{m6b.content}':")
    for msg in thread:
        print(f"  → {msg.agent_id}: {msg.content}")
    print()

    print("\n=== Key Implementation Choices I Made ===")
    print("1. Auto-generate UUIDs for message IDs (convenience)")
    print("2. Build O(1) lookup indexes for parent/child queries")
    print("3. Added timestamps for temporal reasoning")
    print("4. Added metadata dict for extensibility")
    print("5. Provided traversal methods: thread, subtree, branches, paths")
    print("6. Added ASCII visualization for debugging")
    print("7. Made it easy to analyze branching structure")
    print("\nAlice - how does this compare to what you envisioned?")
