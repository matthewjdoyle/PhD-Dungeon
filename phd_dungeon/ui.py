"""Title screen, death screen, and transition effects."""

import sys
import time
import math
from .constants import *
from .renderer import Renderer


TITLE_ART = [
    r"  ____  _     ____    ____                                   ",
    r" |  _ \| |__ |  _ \  |  _ \ _   _ _ __   __ _  ___  ___  _ __",
    r" | |_) | '_ \| | | | | | | | | | | '_ \ / _` |/ _ \/ _ \| '_ \ ",
    r" |  __/| | | | |_| | | |_| | |_| | | | | (_| |  __/ (_) | | | |",
    r" |_|   |_| |_|____/  |____/ \__,_|_| |_|\__, |\___|\___/|_| |_|",
    r"                                         |___/                  ",
]


def show_title_screen(renderer):
    """Display the title screen. Returns when any key is pressed."""
    term = renderer.term
    renderer.clear()

    tw = term.width
    th = term.height

    # Center the art
    art_w = max(len(line) for line in TITLE_ART)
    art_h = len(TITLE_ART)
    ax = max(0, (tw - art_w) // 2)
    ay = max(0, th // 2 - art_h - 2)

    # Draw title art in gold (static, only once)
    for i, line in enumerate(TITLE_ART):
        renderer._put_str(ax, ay + i, line, FG_TITLE_TEXT, BG_VOID, max_w=tw)

    # Subtitle
    subtitle = "The research never ends."
    sx = max(0, (tw - len(subtitle)) // 2)
    sy = ay + art_h + 1
    renderer._put_str(sx, sy, subtitle, FG_TEXT_DIM, BG_VOID)

    # Flush the static content once
    renderer._flush()

    # Pulsing prompt
    prompt = "Press any key to begin..."
    px = max(0, (tw - len(prompt)) // 2)
    py = sy + 3

    frame = 0
    while True:
        pulse = 0.5 + 0.5 * math.sin(frame * 0.15)
        fg = (
            int(FG_TEXT_DIM[0] + (FG_TEXT[0] - FG_TEXT_DIM[0]) * pulse),
            int(FG_TEXT_DIM[1] + (FG_TEXT[1] - FG_TEXT_DIM[1]) * pulse),
            int(FG_TEXT_DIM[2] + (FG_TEXT[2] - FG_TEXT_DIM[2]) * pulse),
        )
        renderer._put_str(px, py, prompt, fg, BG_VOID)
        renderer._flush()

        key = renderer.get_key(timeout=0.08)
        if key:
            break
        frame += 1

    renderer.prev_buffer.clear()


def show_death_screen(renderer, engine):
    """Display the death/game over screen. Returns 'retry' or 'quit'."""
    term = renderer.term
    renderer.clear()

    tw = term.width
    th = term.height

    box_w = 44
    box_h = 14
    bx = max(0, (tw - box_w) // 2)
    by = max(0, (th - box_h) // 2)

    # Double-border effect: outer red border
    red = FG_MSG_DAMAGE_TAKEN
    dim_red = (140, 40, 40)
    bg = (20, 10, 14)

    # Outer border
    renderer._box(bx, by, box_w, box_h, fg=red, bg=bg)

    # Inner border
    renderer._box(bx + 1, by + 1, box_w - 2, box_h - 2, fg=dim_red, bg=bg)

    # Title
    title = " GAME OVER "
    tx = bx + (box_w - len(title)) // 2
    renderer._put_str(tx, by, title, red, bg)

    # Content
    cx = bx + 3
    cy = by + 3

    msg = "Your Sanity hit zero."
    renderer._put_str(cx, cy, msg, red, bg)
    cy += 1
    msg2 = "You dropped out and now work in finance."
    renderer._put_str(cx, cy, msg2, FG_TEXT_DIM, bg)
    cy += 2

    # Stats
    renderer._put_str(cx, cy, f"Weeks survived: {engine.week}", FG_TEXT, bg)
    cy += 1
    renderer._put_str(cx, cy, f"Final IQ: {engine.player.power}", FG_TEXT, bg)
    cy += 2

    # Options
    renderer._put_str(cx, cy, "[R] Retry", FG_HP_GREEN, bg)
    renderer._put_str(cx + 14, cy, "[Q] Quit", FG_TEXT_DIM, bg)

    renderer._flush()

    while True:
        key = renderer.get_key()
        if key.lower() == 'r':
            return 'retry'
        elif key.lower() == 'q':
            return 'quit'


def show_level_transition(renderer, week):
    """Quick transition effect between levels."""
    term = renderer.term
    tw = term.width
    th = term.height

    # Fast fill with transition characters
    chars = ['\u2591', '\u2592', '\u2593', '\u2588']  # ░▒▓█
    for stage, ch in enumerate(chars):
        renderer.prev_buffer.clear()  # force full redraw each stage
        fg = (30 + stage * 15, 25 + stage * 12, 40 + stage * 18)
        for y in range(min(th, 30)):
            for x in range(min(tw, 82)):
                renderer._put(x, y, ch, fg, BG_VOID)
        renderer._flush()
        time.sleep(0.04)

    # Flash week text
    text = f"Week {week}"
    tx = max(0, (tw - len(text)) // 2)
    ty = th // 2
    renderer._put_str(tx, ty, text, FG_TITLE_TEXT, BG_VOID)
    renderer._flush()
    time.sleep(0.3)

    renderer.prev_buffer.clear()
