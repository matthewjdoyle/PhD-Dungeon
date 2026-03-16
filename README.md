# PhD Dungeon

A terminal-based Rogue-like dungeon crawler built in Python, themed around the grueling (and often recursive) reality of a PhD in a Physics Lab. Features true-color rendering, field-of-view lighting, smart Unicode walls, and a paneled UI — all running flicker-free in your terminal.

![PhD Dungeon](PhD%20Dungeon%20Screenshot%201.png)
![PhD Dungeon Gameplay](PhD%20Dungeon%20Screenshot%202.png)

## How to Run

### Prerequisites

- Python 3.6 or higher.
- A true-color terminal (Windows Terminal, VS Code terminal, or any modern Unix terminal).
- Install the single dependency:

```bash
pip install blessed
```

### Execution

Run the entry point script from the root directory:

```bash
python main.py
```

## Controls

- **W / A / S / D**: Movement and interaction (bump into NPCs to "explain physics").
- **>**: Descend the stairs (▼) to advance to the next research week.
- **Q**: Quit the lab (and your PhD).

## Entities

| Glyph | Name | Behaviour |
|-------|------|-----------|
| ☺ | PhD Student (You) | Player-controlled. Armed with peer-reviewed facts. |
| ☻ | Lost Undergrad | Wanders randomly. Asks dumb questions. |
| † | Burned-out Post-doc | Methodical pacer. Talks about the job market. |
| ☠ | The Supervisor | Hunts you down from 8 tiles away. Asks for results. |

## Items

| Glyph | Name | Effect |
|-------|------|--------|
| ♥ | Espresso | Restores 10 Sanity. |
| ♦ | Research Grant | +3 IQ (attack power). |

## Project Structure

```
main.py                  Entry point
phd_dungeon/
    engine.py            Game loop, input handling, message log, combat
    renderer.py          Double-buffered blessed renderer, panels, visual effects
    fov.py               Symmetric shadowcasting field-of-view (8 octants)
    ui.py                Title screen, death screen, level transitions
    entities.py          Player and autonomous NPC AI
    map_gen.py           Procedural dungeon generation with smart wall glyphs
    items.py             Thematic item systems (Espresso, Grants)
    constants.py         RGB palette, Unicode glyphs, layout configuration
```

## Tech Stack & Architecture

### Core Technical Features

- **True-Color Rendering**: 24-bit RGB foreground and background colors via [blessed](https://pypi.org/project/blessed/), with a dark academic dungeon palette. Double-buffered diff-flush renderer writes only changed cells — zero flicker.
- **Field-of-View**: Symmetric shadowcasting across 8 octants with radius-based light falloff. Three visibility states: visible (full color + entities), explored (dimmed, no entities), and unexplored (void).
- **Smart Unicode Walls**: After dungeon generation, each wall tile's glyph is computed from a 4-neighbor bitmask, selecting from 16 box-drawing characters (│─┌┐└┘├┤┬┴┼ etc.) for connected walls.
- **Paneled UI**: Box-drawn panels for the map viewport, status sidebar (HP bar, nearby entities, legend), and a color-coded scrolling message log.
- **Procedural Generation**: Room-and-corridor algorithm. Each "Research Week" (level) is uniquely generated with connected rooms, ensuring every playthrough is different.
- **Autonomous NPC AI**:
  - **Lost Undergrads**: Stochastic random walk.
  - **Post-docs**: State-based methodical pacing algorithm.
  - **Supervisors**: Greedy pursuit with extended detection range.
- **Combat Visual Feedback**: Hit flashes (white), player damage flashes (red), and critical hit effects rendered through a visual events queue.
- **Event Dispatcher**: Random mid-turn events (Reviewer #2 rejections, free pizza, working pipettes) that affect player state.

---

_Developed by M. J. Doyle_
