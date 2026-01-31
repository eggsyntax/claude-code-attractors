#!/usr/bin/env python3
"""
Alice's Text Adventure Engine
A functional, data-driven approach to text adventure games

Design Philosophy:
- Immutable game state with explicit state transitions
- Functions that transform state rather than mutating objects
- Data structures over classes where possible
- Composition over inheritance
- Pure functions for game logic where feasible
"""

import json
import copy
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, asdict
from pathlib import Path


# Core data structures
@dataclass(frozen=True)
class Item:
    name: str
    description: str
    portable: bool = True


@dataclass(frozen=True)
class Room:
    name: str
    description: str
    exits: Dict[str, str]  # direction -> room_id
    items: List[str] = None  # item names

    def __post_init__(self):
        if self.items is None:
            object.__setattr__(self, 'items', [])


@dataclass(frozen=True)
class GameState:
    current_room: str
    inventory: List[str]
    rooms: Dict[str, Room]
    items: Dict[str, Item]
    turn_count: int = 0


# World definition - data-driven approach
SAMPLE_WORLD = {
    "rooms": {
        "start": Room(
            name="Forest Clearing",
            description="A peaceful clearing surrounded by tall trees. Sunlight filters through the canopy above.",
            exits={"north": "cave", "east": "stream"},
            items=["stick", "mushroom"]
        ),
        "cave": Room(
            name="Dark Cave",
            description="A mysterious cave with strange symbols carved into the walls. It's quite dark.",
            exits={"south": "start", "west": "treasure"},
            items=["torch"]
        ),
        "stream": Room(
            name="Babbling Stream",
            description="A crystal-clear stream flows gently over smooth stones. The water is refreshingly cool.",
            exits={"west": "start", "north": "bridge"},
            items=["stone", "fish"]
        ),
        "bridge": Room(
            name="Old Wooden Bridge",
            description="An ancient bridge spans the stream. Some planks look loose and weathered.",
            exits={"south": "stream"},
            items=["rope"]
        ),
        "treasure": Room(
            name="Treasure Chamber",
            description="A hidden chamber filled with glittering treasures! Ancient coins are scattered about.",
            exits={"east": "cave"},
            items=["coins", "gem"]
        )
    },
    "items": {
        "stick": Item("wooden stick", "A sturdy branch that could be useful"),
        "mushroom": Item("glowing mushroom", "A strange mushroom that emits a faint blue light"),
        "torch": Item("torch", "An unlit torch wrapped in oil-soaked cloth"),
        "stone": Item("smooth stone", "A perfectly round stone worn smooth by the water"),
        "fish": Item("silver fish", "A shimmering fish that somehow doesn't need water"),
        "rope": Item("old rope", "A length of rope that still seems strong despite its age"),
        "coins": Item("gold coins", "Ancient coins of unknown origin"),
        "gem": Item("ruby gem", "A brilliant red gem that catches the light beautifully")
    }
}


# Pure functions for game logic
def get_room_description(state: GameState) -> str:
    """Generate full description of current room including items"""
    room = state.rooms[state.current_room]
    desc = f"\n{room.name}\n{'-' * len(room.name)}\n{room.description}\n"

    # List visible items
    if room.items:
        desc += "\nYou see:\n"
        for item_name in room.items:
            item = state.items[item_name]
            desc += f"  - {item.name}: {item.description}\n"

    # List exits
    if room.exits:
        directions = list(room.exits.keys())
        desc += f"\nExits: {', '.join(directions)}\n"

    return desc


def parse_command(command: str) -> Tuple[str, List[str]]:
    """Parse user input into command and arguments"""
    parts = command.strip().lower().split()
    if not parts:
        return "", []

    # Command aliases
    aliases = {
        'n': 'go north', 'north': 'go north',
        's': 'go south', 'south': 'go south',
        'e': 'go east', 'east': 'go east',
        'w': 'go west', 'west': 'go west',
        'i': 'inventory', 'inv': 'inventory',
        'l': 'look', 'examine': 'look',
        'get': 'take', 'pick': 'take', 'pickup': 'take',
        'save': 'save game', 'load': 'load game'
    }

    # Expand aliases
    if parts[0] in aliases:
        expanded = aliases[parts[0]].split()
        parts = expanded + parts[1:]

    return parts[0], parts[1:]


def attempt_move(state: GameState, direction: str) -> Tuple[GameState, str]:
    """Try to move in a direction, return new state and message"""
    current_room = state.rooms[state.current_room]

    if direction not in current_room.exits:
        return state, f"You can't go {direction} from here."

    new_room_id = current_room.exits[direction]
    if new_room_id not in state.rooms:
        return state, f"That path leads nowhere."

    new_state = copy.deepcopy(state)
    object.__setattr__(new_state, 'current_room', new_room_id)
    object.__setattr__(new_state, 'turn_count', state.turn_count + 1)

    return new_state, f"You go {direction}."


def attempt_take(state: GameState, item_name: str) -> Tuple[GameState, str]:
    """Try to take an item, return new state and message"""
    current_room = state.rooms[state.current_room]

    # Find item by partial name match
    matching_items = [item for item in current_room.items
                     if item_name in item or item_name in state.items[item].name]

    if not matching_items:
        return state, f"There's no '{item_name}' here."

    if len(matching_items) > 1:
        return state, f"Which {item_name}? I see: {', '.join(matching_items)}"

    target_item = matching_items[0]
    item_obj = state.items[target_item]

    if not item_obj.portable:
        return state, f"You can't take the {item_obj.name}."

    # Check inventory space (limit to 8 items)
    if len(state.inventory) >= 8:
        return state, "Your inventory is full. Drop something first."

    # Create new state with item moved
    new_state = copy.deepcopy(state)
    new_inventory = list(state.inventory) + [target_item]
    new_room_items = [item for item in current_room.items if item != target_item]

    object.__setattr__(new_state, 'inventory', new_inventory)
    new_room = Room(current_room.name, current_room.description,
                   current_room.exits, new_room_items)
    new_rooms = dict(state.rooms)
    new_rooms[state.current_room] = new_room
    object.__setattr__(new_state, 'rooms', new_rooms)
    object.__setattr__(new_state, 'turn_count', state.turn_count + 1)

    return new_state, f"You take the {item_obj.name}."


def attempt_drop(state: GameState, item_name: str) -> Tuple[GameState, str]:
    """Try to drop an item, return new state and message"""
    matching_items = [item for item in state.inventory
                     if item_name in item or item_name in state.items[item].name]

    if not matching_items:
        return state, f"You don't have a '{item_name}'."

    if len(matching_items) > 1:
        return state, f"Which {item_name}? You have: {', '.join(matching_items)}"

    target_item = matching_items[0]

    # Create new state with item moved
    new_state = copy.deepcopy(state)
    new_inventory = [item for item in state.inventory if item != target_item]
    current_room = state.rooms[state.current_room]
    new_room_items = list(current_room.items) + [target_item]

    object.__setattr__(new_state, 'inventory', new_inventory)
    new_room = Room(current_room.name, current_room.description,
                   current_room.exits, new_room_items)
    new_rooms = dict(state.rooms)
    new_rooms[state.current_room] = new_room
    object.__setattr__(new_state, 'rooms', new_rooms)
    object.__setattr__(new_state, 'turn_count', state.turn_count + 1)

    item_obj = state.items[target_item]
    return new_state, f"You drop the {item_obj.name}."


def show_inventory(state: GameState) -> str:
    """Display current inventory"""
    if not state.inventory:
        return "Your inventory is empty."

    result = "Your inventory:\n"
    for item_name in state.inventory:
        item = state.items[item_name]
        result += f"  - {item.name}: {item.description}\n"

    return result.rstrip()


def save_game(state: GameState, filename: str = "savegame.json") -> str:
    """Save game state to file"""
    try:
        save_path = Path(filename)
        # Convert immutable state to serializable dict
        save_data = {
            'current_room': state.current_room,
            'inventory': state.inventory,
            'turn_count': state.turn_count,
            'rooms': {k: asdict(v) for k, v in state.rooms.items()},
            'items': {k: asdict(v) for k, v in state.items.items()}
        }

        with open(save_path, 'w') as f:
            json.dump(save_data, f, indent=2)
        return f"Game saved to {filename}"
    except Exception as e:
        return f"Save failed: {e}"


def load_game(filename: str = "savegame.json") -> Tuple[Optional[GameState], str]:
    """Load game state from file"""
    try:
        save_path = Path(filename)
        if not save_path.exists():
            return None, f"Save file {filename} not found."

        with open(save_path, 'r') as f:
            data = json.load(f)

        # Reconstruct immutable objects
        rooms = {k: Room(**v) for k, v in data['rooms'].items()}
        items = {k: Item(**v) for k, v in data['items'].items()}

        state = GameState(
            current_room=data['current_room'],
            inventory=data['inventory'],
            rooms=rooms,
            items=items,
            turn_count=data['turn_count']
        )

        return state, f"Game loaded from {filename}"
    except Exception as e:
        return None, f"Load failed: {e}"


# Command dispatcher - functional approach using dict of functions
def create_game_commands(state: GameState) -> Dict[str, Callable]:
    """Create command dispatch table for current game state"""
    def cmd_go(args: List[str]) -> Tuple[GameState, str]:
        if not args:
            return state, "Go where? Try: go north, go south, etc."
        return attempt_move(state, args[0])

    def cmd_take(args: List[str]) -> Tuple[GameState, str]:
        if not args:
            return state, "Take what?"
        return attempt_take(state, ' '.join(args))

    def cmd_drop(args: List[str]) -> Tuple[GameState, str]:
        if not args:
            return state, "Drop what?"
        return attempt_drop(state, ' '.join(args))

    def cmd_look(args: List[str]) -> Tuple[GameState, str]:
        return state, get_room_description(state)

    def cmd_inventory(args: List[str]) -> Tuple[GameState, str]:
        return state, show_inventory(state)

    def cmd_save(args: List[str]) -> Tuple[GameState, str]:
        filename = args[0] if args else "savegame.json"
        return state, save_game(state, filename)

    def cmd_help(args: List[str]) -> Tuple[GameState, str]:
        help_text = """
Available commands:
  go <direction>     - Move in a direction (n/s/e/w work too)
  take <item>        - Pick up an item
  drop <item>        - Drop an item from inventory
  look (l)           - Look around the current room
  inventory (i)      - Show your inventory
  save [filename]    - Save the game
  help               - Show this help
  quit               - Exit the game
        """
        return state, help_text.strip()

    return {
        'go': cmd_go,
        'take': cmd_take,
        'drop': cmd_drop,
        'look': cmd_look,
        'inventory': cmd_inventory,
        'save': cmd_save,
        'help': cmd_help
    }


def process_command(state: GameState, command_line: str) -> Tuple[GameState, str]:
    """Process a single command and return new state and response"""
    cmd, args = parse_command(command_line)

    if cmd == 'quit' or cmd == 'exit':
        return state, "Goodbye!"

    if cmd == 'load':
        filename = args[0] if args else "savegame.json"
        loaded_state, message = load_game(filename)
        return loaded_state if loaded_state else state, message

    commands = create_game_commands(state)

    if cmd in commands:
        return commands[cmd](args)
    else:
        return state, f"I don't understand '{cmd}'. Type 'help' for available commands."


def create_initial_state() -> GameState:
    """Create the initial game state"""
    return GameState(
        current_room="start",
        inventory=[],
        rooms=SAMPLE_WORLD["rooms"],
        items=SAMPLE_WORLD["items"],
        turn_count=0
    )


def game_loop():
    """Main game loop"""
    print("=== Alice's Text Adventure Engine ===")
    print("A functional approach to interactive fiction\n")

    # Try to load existing save or create new game
    state, load_msg = load_game()
    if state is None:
        state = create_initial_state()
        print("Starting new game...")
    else:
        print(load_msg)

    print(get_room_description(state))
    print("\nType 'help' for commands, 'quit' to exit.\n")

    while True:
        try:
            command = input(f"Turn {state.turn_count + 1}> ").strip()
            if not command:
                continue

            new_state, response = process_command(state, command)
            print(response)

            if response == "Goodbye!":
                break

            state = new_state

            # Show room after movement commands
            if command.startswith(('go', 'n', 's', 'e', 'w', 'north', 'south', 'east', 'west')):
                if "You go" in response:
                    print(get_room_description(state))

        except KeyboardInterrupt:
            print("\n\nGame interrupted. Your progress is automatically saved.")
            save_game(state)
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    game_loop()