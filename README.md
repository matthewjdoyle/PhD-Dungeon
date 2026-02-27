# PhD Dungeon

A terminal-based Rogue-like dungeon crawler built in pure Python, themed around the grueling (and often recursive) reality of a PhD in a Physics Lab.

![PhD Dungeon Gameplay](PhD%20Dungeon%20Screenshot%201.png)

## How to Run

### Prerequisites

- Python 3.6 or higher.
- A terminal that supports ANSI escape codes (Windows Terminal, PowerShell, CMD, or any Unix-based terminal).

### Execution

The project is modularised into a Python package. To play the game, run the entry point script from the root directory:

```bash
python main.py
```

### Project Structure

- `main.py`: The entry point for the application.
- `phd_dungeon/`: The core package containing game logic.
  - `engine.py`: Orchestrates the game loop, events, and rendering.
  - `entities.py`: Logic for the Player and autonomous NPC AI.
  - `map_gen.py`: Procedural dungeon generation algorithms.
  - `items.py`: Thematic item systems (Espresso, Grants).
  - `constants.py`: Centralised configuration and ANSI color definitions.

## Controls

- **W / A / S / D**: Movement and interaction (bumping into NPCs to "explain physics").
- **>**: Submit your research at the Portal (`E`) to advance to the next week.
- **Q**: Quit the lab (and your PhD).

## Tech Stack & Architecture

This project was built to demonstrate a highly portable, dependency-free Python application that handles real-time input and rendering in a CLI environment.

### Core Technical Features:

- **Zero Dependencies**: Written using only the Python standard library. No `curses` or external packages required, ensuring it runs out-of-the-box on Windows via `msvcrt`.
- **Procedural Generation**: Utilises a customized Room-and-Corridor algorithm. Each "Research Week" (level) is uniquely generated with a connected graph of nodes, ensuring every playthrough is different.
- **Entity Component System (Simplified)**: Entities (Player, Undergrads, Supervisors) are managed through a class-based system that handles state, stats scaling, and specific AI behaviors.
- **Autonomous NPC AI**:
  - **Lost Undergrads**: Stochastic "Random Walk" behaviour.
  - **Post-docs**: State-based "Methodical Pacing" algorithm.
  - **Supervisors**: Range-limited "A\* Pathfinding" (Greedy-style) to track and engage the player.
- **ANSI Rendering Engine**: A custom-built rendering loop that leverages ANSI escape codes for colorized output and screen refreshing, optimised to minimise flicker in a standard terminal.
- **Event Dispatcher**: A lightweight random event system that triggers mid-turn effects, affecting player state and persistence.

---

_Developed by M. J. Doyle_
