"""
Event-Driven Text Adventure Engine
A third approach that treats the game as a stream of events and reactions.
"""

from dataclasses import dataclass, replace
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import json

# Events - Pure data describing what happened
@dataclass(frozen=True)
class Event:
    """Base class for all game events"""
    pass

@dataclass(frozen=True)
class CommandEntered(Event):
    command: str
    args: List[str]

@dataclass(frozen=True)
class PlayerMoved(Event):
    from_room: str
    to_room: str
    direction: str

@dataclass(frozen=True)
class ItemPickedUp(Event):
    item: str
    from_room: str

@dataclass(frozen=True)
class ItemDropped(Event):
    item: str
    to_room: str

@dataclass(frozen=True)
class GameStateRequested(Event):
    pass

@dataclass(frozen=True)
class InvalidCommand(Event):
    message: str

# Game State - Immutable data structures
@dataclass(frozen=True)
class GameState:
    current_room: str
    player_inventory: tuple[str, ...]
    room_items: Dict[str, tuple[str, ...]]
    room_connections: Dict[str, Dict[str, str]]
    room_descriptions: Dict[str, str]

# Event Handlers - Pure functions that transform state
class EventBus:
    def __init__(self):
        self.handlers: Dict[type, List[Callable]] = {}
        self.middleware: List[Callable] = []

    def subscribe(self, event_type: type, handler: Callable):
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

    def add_middleware(self, middleware: Callable):
        self.middleware.append(middleware)

    def publish(self, event: Event, state: GameState) -> tuple[GameState, List[Event]]:
        # Apply middleware (for logging, validation, etc.)
        for middleware in self.middleware:
            event, state = middleware(event, state)

        # Find and execute handlers
        event_type = type(event)
        if event_type in self.handlers:
            new_events = []
            for handler in self.handlers[event_type]:
                result = handler(event, state)
                if isinstance(result, tuple):
                    state, events = result
                    new_events.extend(events)
                else:
                    state = result
            return state, new_events
        return state, []

# Command Parser - Converts strings to events
class CommandParser:
    def __init__(self):
        self.aliases = {
            'n': 'north', 's': 'south', 'e': 'east', 'w': 'west',
            'i': 'inventory', 'inv': 'inventory',
            'get': 'take', 'pickup': 'take',
            'l': 'look'
        }

    def parse(self, command_str: str) -> Event:
        parts = command_str.strip().lower().split()
        if not parts:
            return InvalidCommand("Please enter a command.")

        command = self.aliases.get(parts[0], parts[0])
        args = parts[1:]

        return CommandEntered(command, args)

# Game Handlers - Business logic as event reactions
def handle_command_entered(event: CommandEntered, state: GameState) -> tuple[GameState, List[Event]]:
    """Route commands to specific actions"""
    command = event.command
    args = event.args

    if command in ['north', 'south', 'east', 'west']:
        return state, [PlayerMoved(state.current_room, "", command)]
    elif command == 'take' and args:
        return state, [ItemPickedUp(' '.join(args), state.current_room)]
    elif command == 'drop' and args:
        return state, [ItemDropped(' '.join(args), state.current_room)]
    elif command in ['inventory', 'look']:
        return state, [GameStateRequested()]
    else:
        return state, [InvalidCommand(f"Unknown command: {command}")]

def handle_player_moved(event: PlayerMoved, state: GameState) -> GameState:
    """Handle room navigation"""
    current_room = state.current_room
    direction = event.direction

    if (current_room in state.room_connections and
        direction in state.room_connections[current_room]):
        new_room = state.room_connections[current_room][direction]
        new_state = replace(state, current_room=new_room)
        print(f"\nYou go {direction}.")
        print(f"\n{state.room_descriptions[new_room]}")

        # Show items in room
        if new_room in state.room_items and state.room_items[new_room]:
            print(f"Items here: {', '.join(state.room_items[new_room])}")

        return new_state
    else:
        print(f"You can't go {direction} from here.")
        return state

def handle_item_picked_up(event: ItemPickedUp, state: GameState) -> GameState:
    """Handle item pickup"""
    item = event.item
    room = event.from_room

    if room in state.room_items and item in state.room_items[room]:
        # Remove item from room
        room_items = dict(state.room_items)
        room_items[room] = tuple(i for i in room_items[room] if i != item)

        # Add to inventory
        new_inventory = state.player_inventory + (item,)

        new_state = replace(state,
                          player_inventory=new_inventory,
                          room_items=room_items)
        print(f"You take the {item}.")
        return new_state
    else:
        print(f"There's no {item} here.")
        return state

def handle_item_dropped(event: ItemDropped, state: GameState) -> GameState:
    """Handle item drop"""
    item = event.item
    room = event.to_room

    if item in state.player_inventory:
        # Remove from inventory
        new_inventory = tuple(i for i in state.player_inventory if i != item)

        # Add to room
        room_items = dict(state.room_items)
        if room not in room_items:
            room_items[room] = ()
        room_items[room] = room_items[room] + (item,)

        new_state = replace(state,
                          player_inventory=new_inventory,
                          room_items=room_items)
        print(f"You drop the {item}.")
        return new_state
    else:
        print(f"You don't have a {item}.")
        return state

def handle_game_state_requested(event: GameStateRequested, state: GameState) -> GameState:
    """Display current game state"""
    print(f"\n{state.room_descriptions[state.current_room]}")

    if state.current_room in state.room_items and state.room_items[state.current_room]:
        print(f"Items here: {', '.join(state.room_items[state.current_room])}")

    if state.player_inventory:
        print(f"Inventory: {', '.join(state.player_inventory)}")
    else:
        print("Inventory: empty")

    return state

def handle_invalid_command(event: InvalidCommand, state: GameState) -> GameState:
    """Handle invalid commands"""
    print(event.message)
    return state

# Logging middleware
def logging_middleware(event: Event, state: GameState) -> tuple[Event, GameState]:
    """Log all events for debugging"""
    print(f"[DEBUG] Event: {event}")
    return event, state

# Game Engine
class EventDrivenGame:
    def __init__(self):
        self.event_bus = EventBus()
        self.parser = CommandParser()

        # Subscribe handlers
        self.event_bus.subscribe(CommandEntered, handle_command_entered)
        self.event_bus.subscribe(PlayerMoved, handle_player_moved)
        self.event_bus.subscribe(ItemPickedUp, handle_item_picked_up)
        self.event_bus.subscribe(ItemDropped, handle_item_dropped)
        self.event_bus.subscribe(GameStateRequested, handle_game_state_requested)
        self.event_bus.subscribe(InvalidCommand, handle_invalid_command)

        # Add middleware (uncomment for debugging)
        # self.event_bus.add_middleware(logging_middleware)

        # Initialize game state
        self.state = GameState(
            current_room="entrance",
            player_inventory=(),
            room_items={
                "entrance": ("key",),
                "library": ("book", "candle"),
                "garden": ("flower",),
                "treasure": ()
            },
            room_connections={
                "entrance": {"north": "library", "east": "garden"},
                "library": {"south": "entrance", "west": "treasure"},
                "garden": {"west": "entrance"},
                "treasure": {"east": "library"}
            },
            room_descriptions={
                "entrance": "You're in the entrance hall. Exits: north (library), east (garden)",
                "library": "You're in a dusty library. Exits: south (entrance), west (treasure room)",
                "garden": "You're in a beautiful garden. Exits: west (entrance)",
                "treasure": "You're in the treasure room! Exits: east (library)"
            }
        )

    def process_command(self, command_str: str):
        """Process a single command, potentially generating a cascade of events"""
        event = self.parser.parse(command_str)
        events_to_process = [event]

        while events_to_process:
            current_event = events_to_process.pop(0)
            self.state, new_events = self.event_bus.publish(current_event, self.state)
            events_to_process.extend(new_events)

    def run(self):
        """Main game loop"""
        print("Welcome to the Event-Driven Text Adventure!")
        print("Commands: north/n, south/s, east/e, west/w, take <item>, drop <item>, inventory/i, look/l")
        print(f"\n{self.state.room_descriptions[self.state.current_room]}")

        if self.state.current_room in self.state.room_items and self.state.room_items[self.state.current_room]:
            print(f"Items here: {', '.join(self.state.room_items[self.state.current_room])}")

        while True:
            try:
                command = input("\n> ").strip()
                if command.lower() in ['quit', 'exit']:
                    print("Thanks for playing!")
                    break
                if command:
                    self.process_command(command)
            except KeyboardInterrupt:
                print("\nThanks for playing!")
                break

if __name__ == "__main__":
    game = EventDrivenGame()
    game.run()