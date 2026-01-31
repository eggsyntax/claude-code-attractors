#!/usr/bin/env python3
"""
Bob's Text Adventure Game Engine
A class-based approach to building a flexible text adventure framework
"""

import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"
    UP = "up"
    DOWN = "down"


@dataclass
class Item:
    """Represents an item in the game world"""
    name: str
    description: str
    takeable: bool = True

    def __str__(self):
        return self.name


class Room:
    """Represents a location in the game world"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.exits: Dict[Direction, str] = {}  # Direction -> room_id
        self.items: List[Item] = []
        self.visited = False

    def add_exit(self, direction: Direction, room_id: str):
        """Add an exit to another room"""
        self.exits[direction] = room_id

    def add_item(self, item: Item):
        """Add an item to this room"""
        self.items.append(item)

    def remove_item(self, item_name: str) -> Optional[Item]:
        """Remove and return an item by name"""
        for item in self.items:
            if item.name.lower() == item_name.lower():
                self.items.remove(item)
                return item
        return None

    def get_description(self) -> str:
        """Get the full room description including items and exits"""
        desc = self.description

        if self.items:
            item_names = [item.name for item in self.items]
            desc += f"\n\nYou see: {', '.join(item_names)}"

        if self.exits:
            exit_names = [direction.value for direction in self.exits.keys()]
            desc += f"\n\nExits: {', '.join(exit_names)}"

        return desc


class Player:
    """Represents the player state"""

    def __init__(self, starting_room: str):
        self.current_room = starting_room
        self.inventory: List[Item] = []
        self.max_inventory = 10

    def add_to_inventory(self, item: Item) -> bool:
        """Add item to inventory if there's space"""
        if len(self.inventory) >= self.max_inventory:
            return False
        self.inventory.append(item)
        return True

    def remove_from_inventory(self, item_name: str) -> Optional[Item]:
        """Remove and return item from inventory"""
        for item in self.inventory:
            if item.name.lower() == item_name.lower():
                self.inventory.remove(item)
                return item
        return None

    def has_item(self, item_name: str) -> bool:
        """Check if player has an item"""
        return any(item.name.lower() == item_name.lower() for item in self.inventory)

    def get_inventory_description(self) -> str:
        """Get a description of the player's inventory"""
        if not self.inventory:
            return "You are carrying nothing."

        item_names = [item.name for item in self.inventory]
        return f"You are carrying: {', '.join(item_names)}"


class CommandParser:
    """Parses and interprets player commands"""

    def __init__(self):
        # Define command aliases
        self.direction_aliases = {
            'n': Direction.NORTH, 'north': Direction.NORTH,
            's': Direction.SOUTH, 'south': Direction.SOUTH,
            'e': Direction.EAST, 'east': Direction.EAST,
            'w': Direction.WEST, 'west': Direction.WEST,
            'u': Direction.UP, 'up': Direction.UP,
            'd': Direction.DOWN, 'down': Direction.DOWN
        }

        self.action_aliases = {
            'get': 'take', 'pick up': 'take', 'grab': 'take',
            'drop': 'drop', 'put down': 'drop',
            'look': 'look', 'examine': 'look', 'l': 'look',
            'inventory': 'inventory', 'inv': 'inventory', 'i': 'inventory',
            'help': 'help', 'h': 'help', '?': 'help',
            'quit': 'quit', 'exit': 'quit', 'q': 'quit',
            'save': 'save', 'load': 'load'
        }

    def parse(self, command: str) -> tuple[str, List[str]]:
        """Parse a command into action and arguments"""
        parts = command.lower().strip().split()
        if not parts:
            return 'unknown', []

        # Check for movement commands
        if parts[0] in self.direction_aliases:
            return 'move', [self.direction_aliases[parts[0]].value]

        # Check for other actions
        action = self.action_aliases.get(parts[0], parts[0])
        args = parts[1:] if len(parts) > 1 else []

        return action, args


class GameEngine:
    """Main game engine that coordinates all components"""

    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.player: Optional[Player] = None
        self.parser = CommandParser()
        self.running = False
        self.save_file = "game_save.json"

    def add_room(self, room_id: str, room: Room):
        """Add a room to the game world"""
        self.rooms[room_id] = room

    def start_game(self, starting_room: str):
        """Initialize and start the game"""
        if starting_room not in self.rooms:
            raise ValueError(f"Starting room '{starting_room}' not found")

        self.player = Player(starting_room)
        self.running = True

        print("=== Welcome to Bob's Text Adventure Engine ===")
        print("Type 'help' for available commands.")
        print()

        self._look()

    def process_command(self, command: str) -> bool:
        """Process a player command. Returns False if game should quit."""
        action, args = self.parser.parse(command)

        if action == 'quit':
            return False
        elif action == 'help':
            self._show_help()
        elif action == 'move':
            self._move(args[0] if args else '')
        elif action == 'look':
            if args:
                self._examine(args[0])
            else:
                self._look()
        elif action == 'take':
            self._take(args[0] if args else '')
        elif action == 'drop':
            self._drop(args[0] if args else '')
        elif action == 'inventory':
            self._inventory()
        elif action == 'save':
            self._save_game()
        elif action == 'load':
            self._load_game()
        else:
            print(f"I don't understand '{command}'. Type 'help' for available commands.")

        return True

    def _look(self):
        """Display the current room description"""
        room = self.rooms[self.player.current_room]
        print(f"\n--- {room.name} ---")
        print(room.get_description())
        room.visited = True

    def _move(self, direction: str):
        """Move the player to a different room"""
        try:
            direction_enum = Direction(direction)
        except ValueError:
            print(f"'{direction}' is not a valid direction.")
            return

        room = self.rooms[self.player.current_room]
        if direction_enum not in room.exits:
            print(f"You can't go {direction} from here.")
            return

        new_room_id = room.exits[direction_enum]
        if new_room_id not in self.rooms:
            print(f"Error: Room '{new_room_id}' not found!")
            return

        self.player.current_room = new_room_id
        print(f"You go {direction}.")
        self._look()

    def _take(self, item_name: str):
        """Take an item from the current room"""
        if not item_name:
            print("Take what?")
            return

        room = self.rooms[self.player.current_room]
        item = room.remove_item(item_name)

        if not item:
            print(f"There is no '{item_name}' here.")
            return

        if not item.takeable:
            room.add_item(item)  # Put it back
            print(f"You can't take the {item_name}.")
            return

        if not self.player.add_to_inventory(item):
            room.add_item(item)  # Put it back
            print("You can't carry any more items.")
            return

        print(f"You take the {item_name}.")

    def _drop(self, item_name: str):
        """Drop an item in the current room"""
        if not item_name:
            print("Drop what?")
            return

        item = self.player.remove_from_inventory(item_name)
        if not item:
            print(f"You don't have a '{item_name}'.")
            return

        room = self.rooms[self.player.current_room]
        room.add_item(item)
        print(f"You drop the {item_name}.")

    def _inventory(self):
        """Show the player's inventory"""
        print(self.player.get_inventory_description())

    def _examine(self, target: str):
        """Examine an item or room feature"""
        # Check inventory first
        for item in self.player.inventory:
            if item.name.lower() == target.lower():
                print(item.description)
                return

        # Check room items
        room = self.rooms[self.player.current_room]
        for item in room.items:
            if item.name.lower() == target.lower():
                print(item.description)
                return

        print(f"You don't see a '{target}' here.")

    def _show_help(self):
        """Display available commands"""
        help_text = """
Available commands:
  Movement: north, south, east, west, up, down (or n, s, e, w, u, d)
  Actions: take <item>, drop <item>, look [item], inventory
  Game: help, save, load, quit

Examples:
  north (or n) - move north
  take sword - pick up the sword
  look - examine your surroundings
  inventory - see what you're carrying
  save - save your game progress
        """
        print(help_text)

    def _save_game(self):
        """Save the current game state"""
        try:
            game_state = {
                'player_room': self.player.current_room,
                'player_inventory': [asdict(item) for item in self.player.inventory],
                'room_states': {}
            }

            # Save room states (items and visited status)
            for room_id, room in self.rooms.items():
                game_state['room_states'][room_id] = {
                    'items': [asdict(item) for item in room.items],
                    'visited': room.visited
                }

            with open(self.save_file, 'w') as f:
                json.dump(game_state, f, indent=2)

            print(f"Game saved to {self.save_file}")

        except Exception as e:
            print(f"Failed to save game: {e}")

    def _load_game(self):
        """Load a saved game state"""
        try:
            if not os.path.exists(self.save_file):
                print("No saved game found.")
                return

            with open(self.save_file, 'r') as f:
                game_state = json.load(f)

            # Restore player state
            self.player.current_room = game_state['player_room']
            self.player.inventory = [Item(**item_data) for item_data in game_state['player_inventory']]

            # Restore room states
            for room_id, room_data in game_state['room_states'].items():
                if room_id in self.rooms:
                    room = self.rooms[room_id]
                    room.items = [Item(**item_data) for item_data in room_data['items']]
                    room.visited = room_data['visited']

            print("Game loaded successfully!")
            self._look()

        except Exception as e:
            print(f"Failed to load game: {e}")


def create_sample_game() -> GameEngine:
    """Create a sample game world for testing"""
    game = GameEngine()

    # Create rooms
    cottage = Room("Cozy Cottage", "A small, warm cottage with wooden furniture and a crackling fireplace.")
    garden = Room("Garden", "A beautiful garden with colorful flowers and a small pond.")
    forest = Room("Dark Forest", "A mysterious forest with tall trees blocking most of the sunlight.")
    clearing = Room("Forest Clearing", "A peaceful clearing in the forest with soft grass and wildflowers.")

    # Set up room connections
    cottage.add_exit(Direction.NORTH, "garden")
    garden.add_exit(Direction.SOUTH, "cottage")
    garden.add_exit(Direction.WEST, "forest")
    forest.add_exit(Direction.EAST, "garden")
    forest.add_exit(Direction.NORTH, "clearing")
    clearing.add_exit(Direction.SOUTH, "forest")

    # Add items
    cottage.add_item(Item("lamp", "A brass oil lamp that gives off a warm glow."))
    cottage.add_item(Item("book", "An old leather-bound book of fairy tales."))
    garden.add_item(Item("flower", "A beautiful red rose with a sweet fragrance."))
    forest.add_item(Item("stick", "A sturdy wooden stick, good for walking."))
    clearing.add_item(Item("gem", "A sparkling blue gem that catches the light."))

    # Add rooms to game
    game.add_room("cottage", cottage)
    game.add_room("garden", garden)
    game.add_room("forest", forest)
    game.add_room("clearing", clearing)

    return game


def main():
    """Main game loop"""
    game = create_sample_game()
    game.start_game("cottage")

    try:
        while game.running:
            command = input("\n> ").strip()
            if not command:
                continue

            if not game.process_command(command):
                print("Thanks for playing!")
                break

    except KeyboardInterrupt:
        print("\nGoodbye!")
    except EOFError:
        print("Goodbye!")


if __name__ == "__main__":
    main()