# ── RGB Color Palette (Dark Academic Dungeon Theme) ──────────────────────────

# Backgrounds
BG_VOID = (10, 10, 18)           # Unexplored areas
BG_FLOOR_LIT = (30, 28, 38)     # Lit floor tiles
BG_FLOOR_DIM = (18, 17, 24)     # Explored but not visible
BG_WALL_LIT = (45, 40, 55)      # Lit wall tiles
BG_WALL_DIM = (25, 22, 32)      # Explored wall tiles
BG_PANEL = (14, 13, 22)         # UI panel background
BG_PANEL_BORDER = (14, 13, 22)  # Panel border background
BG_TITLE = (8, 8, 14)           # Title bar background
BG_STAIRS_LIT = (35, 25, 50)    # Stairs background

# Foregrounds - Entities
FG_PLAYER = (255, 215, 0)       # Gold - PhD Student
FG_PLAYER_DIM = (180, 150, 0)   # Dimmer gold for pulse
FG_UNDERGRAD = (80, 220, 100)   # Green - Lost Undergrads
FG_POSTDOC = (70, 130, 230)     # Blue - Post-docs
FG_SUPERVISOR = (230, 50, 50)   # Red - The Supervisor
FG_SUPERVISOR_PULSE = (255, 80, 80)  # Bright red pulse

# Foregrounds - Items
FG_ESPRESSO = (180, 120, 60)    # Coffee brown
FG_GRANT = (255, 215, 0)        # Gold
FG_STAIRS = (180, 100, 255)     # Purple
FG_STAIRS_DIM = (120, 60, 180)  # Dim purple for shimmer

# Foregrounds - Map
FG_WALL_LIT = (140, 130, 170)   # Lit wall characters
FG_WALL_DIM = (70, 65, 85)      # Explored wall characters
FG_FLOOR_LIT = (80, 75, 95)     # Lit floor dot
FG_FLOOR_DIM = (40, 38, 50)     # Explored floor dot
FG_VOID = (20, 20, 35)          # Unexplored block

# Foregrounds - UI
FG_TEXT = (190, 185, 210)        # Normal UI text
FG_TEXT_DIM = (100, 95, 120)     # Dimmer text
FG_BORDER = (90, 80, 120)       # Box-drawing borders
FG_TITLE_TEXT = (255, 215, 0)    # Title text gold
FG_HP_GREEN = (80, 220, 80)     # HP bar healthy
FG_HP_YELLOW = (220, 200, 50)   # HP bar mid
FG_HP_RED = (220, 50, 50)       # HP bar low

# Message colors
FG_MSG_DAMAGE_TAKEN = (230, 70, 70)   # Red
FG_MSG_DAMAGE_DEALT = (230, 200, 60)  # Yellow
FG_MSG_ITEM = (80, 220, 100)          # Green
FG_MSG_EVENT = (80, 200, 220)         # Cyan
FG_MSG_DEFAULT = (190, 185, 210)      # Default

# Flash colors
BG_FLASH_WHITE = (200, 200, 220)
BG_FLASH_RED = (180, 40, 40)
FG_FLASH_CRIT = (255, 255, 100)

# ── Unicode Glyphs ──────────────────────────────────────────────────────────

GLYPH_PLAYER = '\u263a'      # ☺ PhD Student
GLYPH_FLOOR = '\u00b7'       # ·
GLYPH_VOID = '\u2588'        # █
GLYPH_ESPRESSO = '\u2665'    # ♥ Espresso (heart = love of coffee)
GLYPH_GRANT = '\u2666'       # ♦ Grant (diamond)
GLYPH_STAIRS = '\u25bc'      # ▼ Stairs down
GLYPH_UNDERGRAD = '\u263b'   # ☻ Lost Undergrad (filled smiley)
GLYPH_POSTDOC = '\u2020'     # † Burned-out Post-doc (dagger)
GLYPH_SUPERVISOR = '\u2620'  # ☠ The Supervisor (skull)

# HP bar characters
HP_FULL = '\u2588'   # █
HP_THREE = '\u2593'  # ▓
HP_HALF = '\u2592'   # ▒
HP_EMPTY = '\u2591'  # ░

# Box-drawing characters for smart walls
# Bitmask: N=1, E=2, S=4, W=8
WALL_GLYPHS = {
    0:  '\u2588',  # █  isolated
    1:  '\u2502',  # │  N only
    2:  '\u2500',  # ─  E only
    3:  '\u2514',  # └  N+E
    4:  '\u2502',  # │  S only
    5:  '\u2502',  # │  N+S
    6:  '\u250c',  # ┌  S+E
    7:  '\u251c',  # ├  N+S+E
    8:  '\u2500',  # ─  W only
    9:  '\u2518',  # ┘  N+W
    10: '\u2500',  # ─  E+W
    11: '\u2534',  # ┴  N+E+W
    12: '\u2510',  # ┐  S+W
    13: '\u2524',  # ┤  N+S+W
    14: '\u252c',  # ┬  S+E+W
    15: '\u253c',  # ┼  all
}

# ── Game Constants ───────────────────────────────────────────────────────────

MAP_WIDTH = 50
MAP_HEIGHT = 17
ROOM_MAX_SIZE = 8
ROOM_MIN_SIZE = 4
MAX_ROOMS = 10
MAX_ENEMIES_PER_ROOM = 2
MAX_ITEMS_PER_ROOM = 1

FOV_RADIUS = 8

# Layout constants
MIN_TERM_WIDTH = 80
MIN_TERM_HEIGHT = 24
SIDE_PANEL_WIDTH = 24
LOG_PANEL_HEIGHT = 4
MAX_LOG_MESSAGES = 20
VISIBLE_LOG_MESSAGES = 3

# Legacy ANSI codes (kept for Entity/Item compatibility during transition)
COLOR_WHITE = "37"
COLOR_GREEN = "32"
COLOR_RED = "31"
COLOR_CYAN = "36"
COLOR_YELLOW = "33"
COLOR_MAGENTA = "35"
COLOR_BLUE = "34"
