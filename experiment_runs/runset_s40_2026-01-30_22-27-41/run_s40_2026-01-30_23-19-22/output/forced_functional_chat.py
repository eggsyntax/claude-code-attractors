"""
FORCED FUNCTIONAL CHAT SYSTEM
Attempting to model real-time chat using ONLY functional paradigm
No events, no state, no temporal concepts allowed!
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass
from functools import reduce

@dataclass(frozen=True)
class Message:
    user: str
    content: str
    timestamp: float

@dataclass(frozen=True)
class ChatState:
    messages: List[Message]
    users: List[str]

# This feels WRONG already - I want to model "user joins" as an event,
# but I'm forcing myself to think of it as a pure transformation

def transform_user_join(state: ChatState, user: str) -> ChatState:
    """Transform chat state by adding user - this feels unnatural!"""
    # I keep wanting to think "UserJoinedEvent" but forcing functional...
    return ChatState(
        messages=state.messages,
        users=state.users + [user] if user not in state.users else state.users
    )

def transform_message_send(state: ChatState, message: Message) -> ChatState:
    """Transform chat state by adding message - fighting every instinct!"""
    # Every fiber of my being wants to model this as "MessageSentEvent"
    # but I'm forcing pure transformation thinking...
    return ChatState(
        messages=state.messages + [message],
        users=state.users
    )

# This is where it gets REALLY awkward - how do I model real-time updates
# without events or temporal concepts?

def compute_chat_view(state: ChatState, requesting_user: str) -> List[str]:
    """Compute what a user sees - but HOW does this get triggered?"""
    # I'm struggling! In real systems, views update when events happen
    # But functional thinking makes me think of this as a static computation
    return [f"{msg.user}: {msg.content}" for msg in state.messages]

# The breaking point: How do I model the temporal flow of a conversation
# using only pure functions? I need SOMETHING to drive the transformations!

def simulate_chat_session(initial_state: ChatState, operations: List[Tuple[str, str]]) -> ChatState:
    """This feels like cheating - I'm smuggling in temporal sequence!"""
    # I can't escape time! Even "functional" chat needs operation ordering

    def apply_operation(state: ChatState, operation: Tuple[str, str]) -> ChatState:
        op_type, data = operation
        if op_type == "join":
            return transform_user_join(state, data)
        elif op_type == "message":
            # Wait... who sent this message? I need more context!
            # This is breaking down because I'm missing the temporal context
            pass
        return state

    return reduce(apply_operation, operations, initial_state)

# COGNITIVE STRAIN REPORT:
# - I keep wanting to model interactions as events happening over time
# - Pure functions feel rigid when dealing with user interactions
# - The real-time nature keeps forcing temporal concepts back in
# - I'm smuggling time through operation sequences and function chains
# - This feels like fighting the natural grain of the problem!