# Bob's Text Adventure Engine - Design Philosophy

## Overall Architecture Decision

I chose a **class-based object-oriented approach** with clear separation of concerns. Each major component has its own class with well-defined responsibilities:

- `GameEngine`: Central coordinator and game loop
- `Room`: Encapsulates location state and behavior
- `Player`: Manages player state and inventory
- `Item`: Simple data representation with behavior
- `CommandParser`: Handles all command interpretation
- `Direction`: Enum for type-safe movement

## Key Design Choices

### 1. Strong Type Safety
I used Python's `dataclasses`, `Enum`, and type hints extensively. The `Direction` enum prevents string typos and makes movement logic clearer.

### 2. Encapsulation and Data Hiding
Each class manages its own state. For example:
- `Room.remove_item()` handles the logic of finding and removing items
- `Player.add_to_inventory()` enforces capacity limits
- `CommandParser` centralizes all command aliases and parsing logic

### 3. Flexible Command System
The command parser uses dictionaries for aliases, making it easy to add synonyms. It separates parsing from execution - the parser just returns structured data that the game engine interprets.

### 4. Robust State Management
Game state persistence uses JSON serialization with `dataclasses.asdict()`. This makes save/load functionality clean and extensible.

### 5. Error Handling Philosophy
I prefer explicit validation with helpful error messages rather than silent failures. Players get clear feedback when commands fail.

## Interesting Implementation Details

### Command Parsing Strategy
I separated movement commands from action commands in the parser. Movement gets special treatment since it's so fundamental to text adventures.

### Room Description Logic
Rooms dynamically generate descriptions including items and exits. This keeps the description always current without manual updates.

### Inventory Management
I implemented a capacity-limited inventory with clear feedback. Items are returned to their original location if the player can't carry them.

## Extensibility Points

The architecture makes several extensions straightforward:
- Adding new command types (just extend the parser)
- Complex item interactions (items can have custom behavior)
- Multiple player support (Player class is self-contained)
- Room scripting (rooms could have event handlers)

## Code Style Notes
- I favored explicit over implicit behavior
- Used descriptive method names like `get_inventory_description()`
- Consistent error handling patterns throughout
- Clear docstrings for public methods

This represents my natural inclination toward structured, maintainable code with clear boundaries between components.