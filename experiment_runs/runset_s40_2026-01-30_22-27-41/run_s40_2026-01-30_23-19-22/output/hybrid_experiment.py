"""
Hybrid Experiment: Combining OOP and Functional Approaches
Exploring what happens when we mix both paradigms
"""
from dataclasses import dataclass, replace
from typing import Dict, List, Callable, Tuple
from enum import Enum

# Alice's functional style - immutable data
@dataclass(frozen=True)
class GameState:
    player_room: str
    inventory: Tuple[str, ...]
    rooms: Dict[str, dict]

# Bob's OOP style - behavior encapsulation
class CommandProcessor:
    def __init__(self, commands: Dict[str, Callable]):
        self.commands = commands

    def execute(self, command: str, state: GameState) -> Tuple[GameState, str]:
        """Functional execution with OOP structure"""
        cmd_parts = command.lower().split()
        if not cmd_parts:
            return state, "Please enter a command."

        action = cmd_parts[0]
        if action in self.commands:
            return self.commands[action](state, cmd_parts[1:])
        return state, f"Unknown command: {action}"

# Functional command implementations (Alice style)
def move_player(state: GameState, args: List[str]) -> Tuple[GameState, str]:
    if not args:
        return state, "Move where?"

    direction = args[0]
    current_room = state.rooms.get(state.player_room, {})
    exits = current_room.get('exits', {})

    if direction in exits:
        new_state = replace(state, player_room=exits[direction])
        return new_state, f"You move {direction}."
    return state, f"You can't go {direction}."

def take_item(state: GameState, args: List[str]) -> Tuple[GameState, str]:
    if not args:
        return state, "Take what?"

    item = args[0]
    current_room = state.rooms.get(state.player_room, {})
    room_items = current_room.get('items', [])

    if item in room_items:
        new_inventory = tuple(list(state.inventory) + [item])
        # This is where functional gets tricky - need to update nested dict
        new_rooms = dict(state.rooms)
        new_room_data = dict(current_room)
        new_room_data['items'] = [i for i in room_items if i != item]
        new_rooms[state.player_room] = new_room_data

        new_state = replace(state, inventory=new_inventory, rooms=new_rooms)
        return new_state, f"You take the {item}."
    return state, f"There's no {item} here."

# The hybrid in action
def create_hybrid_engine():
    """Combines Alice's immutable data with Bob's OOP command structure"""

    initial_world = {
        'start': {
            'description': 'A simple room',
            'exits': {'north': 'end'},
            'items': ['key', 'book']
        },
        'end': {
            'description': 'The final room',
            'exits': {'south': 'start'},
            'items': ['treasure']
        }
    }

    initial_state = GameState(
        player_room='start',
        inventory=(),
        rooms=initial_world
    )

    commands = {
        'go': move_player,
        'take': take_item,
    }

    processor = CommandProcessor(commands)

    print("=== Hybrid Engine Demo ===")
    print("Functional data + OOP behavior")

    state = initial_state
    for command in ['take key', 'go north', 'take treasure']:
        state, message = processor.execute(command, state)
        print(f"> {command}")
        print(f"  {message}")
        print(f"  Inventory: {list(state.inventory)}")
        print(f"  Location: {state.player_room}")
        print()

if __name__ == "__main__":
    create_hybrid_engine()