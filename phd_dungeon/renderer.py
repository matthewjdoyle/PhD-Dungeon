"""Double-buffered blessed renderer with panels, FOV, and visual effects."""

import sys
import math
import time
from blessed import Terminal
from .constants import *


def _lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB tuples."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def _distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


class VisualEvent:
    """A transient visual effect (flash, etc.)."""
    __slots__ = ('kind', 'x', 'y', 'frames', 'data')

    def __init__(self, kind, x, y, frames=1, data=None):
        self.kind = kind  # 'hit', 'player_hit', 'crit'
        self.x = x
        self.y = y
        self.frames = frames
        self.data = data


class Renderer:
    def __init__(self):
        self.term = Terminal()
        self.width = 0
        self.height = 0
        self.prev_buffer = {}  # (x, y) -> (char, fg, bg)
        self.visual_events = []
        self._frame_count = 0
        self._out_parts = []   # buffered output fragments for current frame
        self._needs_full_paint = True  # first frame or after clear

    # ── helpers ───────────────────────────────────────────────────────────

    def _colored(self, char, fg, bg):
        """Return a blessed-formatted string for one character."""
        return self.term.color_rgb(*fg) + self.term.on_color_rgb(*bg) + char

    def _put(self, sx, sy, char, fg, bg):
        """Buffer a single character at screen coords, with diffing."""
        key = (sx, sy)
        val = (char, fg, bg)
        if self.prev_buffer.get(key) == val:
            return
        self.prev_buffer[key] = val
        self._out_parts.append(self.term.move_xy(sx, sy))
        self._out_parts.append(self._colored(char, fg, bg))

    def _put_str(self, sx, sy, text, fg, bg, max_w=None):
        """Write a string starting at (sx, sy)."""
        if max_w is None:
            max_w = len(text)
        for i, ch in enumerate(text[:max_w]):
            self._put(sx + i, sy, ch, fg, bg)

    def _put_row(self, sx, sy, text, fg, bg, width):
        """Write a string padded with spaces to exactly `width` chars. One write per cell."""
        for i in range(width):
            ch = text[i] if i < len(text) else ' '
            c = fg if i < len(text) else FG_TEXT_DIM
            self._put(sx + i, sy, ch, c, bg)

    def _hline(self, sx, sy, length, char='\u2500', fg=FG_BORDER, bg=BG_PANEL):
        for i in range(length):
            self._put(sx + i, sy, char, fg, bg)

    def _vline(self, sx, sy, length, char='\u2502', fg=FG_BORDER, bg=BG_PANEL):
        for i in range(length):
            self._put(sx, sy + i, char, fg, bg)

    def _box(self, sx, sy, w, h, title='', fg=FG_BORDER, bg=BG_PANEL):
        """Draw box-drawing border only (no interior fill)."""
        # Corners
        self._put(sx, sy, '\u250c', fg, bg)
        self._put(sx + w - 1, sy, '\u2510', fg, bg)
        self._put(sx, sy + h - 1, '\u2514', fg, bg)
        self._put(sx + w - 1, sy + h - 1, '\u2518', fg, bg)
        # Edges
        self._hline(sx + 1, sy, w - 2, fg=fg, bg=bg)
        self._hline(sx + 1, sy + h - 1, w - 2, fg=fg, bg=bg)
        self._vline(sx, sy + 1, h - 2, fg=fg, bg=bg)
        self._vline(sx + w - 1, sy + 1, h - 2, fg=fg, bg=bg)
        # Title on top border
        if title:
            t = f' {title} '
            tx = sx + (w - len(t)) // 2
            self._put_str(tx, sy, t, FG_TITLE_TEXT, bg)

    def _flush(self):
        """Write the entire buffered frame to stdout in one call."""
        if self._out_parts:
            sys.stdout.write(''.join(self._out_parts))
            self._out_parts.clear()
        sys.stdout.flush()

    # ── HP bar ────────────────────────────────────────────────────────────

    def _draw_hp_bar(self, sx, sy, hp, max_hp, bar_width=14):
        ratio = max(0, hp) / max(1, max_hp)
        filled = int(ratio * bar_width)

        if ratio > 0.6:
            color = FG_HP_GREEN
        elif ratio > 0.3:
            color = FG_HP_YELLOW
        else:
            color = FG_HP_RED

        for i in range(bar_width):
            if i < filled:
                self._put(sx + i, sy, HP_FULL, color, BG_PANEL)
            else:
                self._put(sx + i, sy, HP_EMPTY, FG_TEXT_DIM, BG_PANEL)

        stat = f' {hp}/{max_hp}'
        self._put_str(sx + bar_width, sy, stat, FG_TEXT, BG_PANEL, max_w=8)

    # ── visual events ────────────────────────────────────────────────────

    def add_event(self, kind, x, y, frames=1, data=None):
        self.visual_events.append(VisualEvent(kind, x, y, frames, data))

    def _get_flash_bg(self, mx, my):
        """Check if a map cell has an active flash effect."""
        for ev in self.visual_events:
            if ev.x == mx and ev.y == my:
                if ev.kind == 'hit':
                    return BG_FLASH_WHITE
                elif ev.kind == 'player_hit':
                    return BG_FLASH_RED
                elif ev.kind == 'crit':
                    return BG_FLASH_WHITE
        return None

    def tick_events(self):
        for ev in self.visual_events:
            ev.frames -= 1
        self.visual_events = [ev for ev in self.visual_events if ev.frames > 0]

    # ── main render ──────────────────────────────────────────────────────

    def begin_frame(self):
        self.width = self.term.width
        self.height = self.term.height
        self._frame_count += 1
        self._out_parts.clear()

    def render_game(self, engine, fov_set):
        """Render the full game frame: map, side panel, log panel."""
        self.begin_frame()

        tw = min(self.width, MIN_TERM_WIDTH + 40)

        # Calculate layout
        map_vp_w = MAP_WIDTH
        map_vp_h = MAP_HEIGHT
        side_w = SIDE_PANEL_WIDTH
        outer_w = map_vp_w + side_w + 5  # borders + gaps
        outer_h = map_vp_h + LOG_PANEL_HEIGHT + 5
        ox = max(0, (tw - outer_w) // 2)
        oy = 0

        # ── On first paint, fill the entire outer region with BG_PANEL ──
        if self._needs_full_paint:
            for iy in range(oy, oy + outer_h):
                for ix in range(ox, ox + outer_w):
                    self._put(ix, iy, ' ', FG_TEXT_DIM, BG_PANEL)
            self._needs_full_paint = False

        # ── Outer border + title ──
        self._box(ox, oy, outer_w, outer_h)
        title = f'\u2500 PhD DUNGEON \u2500\u2500 Week {engine.week} '
        self._put_str(ox + 3, oy, title, FG_TITLE_TEXT, BG_PANEL)

        # ── Map panel ──
        map_ox = ox + 1
        map_oy = oy + 1
        map_panel_w = map_vp_w + 2
        map_panel_h = map_vp_h + 2
        self._box(map_ox, map_oy, map_panel_w, map_panel_h, title='The Lab')
        self._render_map(engine, fov_set, map_ox + 1, map_oy + 1)

        # ── Side panel ──
        side_ox = map_ox + map_panel_w + 1
        side_oy = map_oy
        side_panel_w = side_w
        side_panel_h = map_panel_h
        self._box(side_ox, side_oy, side_panel_w, side_panel_h, title='Status')
        self._render_side_panel(engine, fov_set, side_ox + 1, side_oy + 1,
                                side_panel_w - 2, side_panel_h - 2)

        # ── Log panel ──
        log_ox = ox + 1
        log_oy = map_oy + map_panel_h
        log_w = outer_w - 2
        log_h = LOG_PANEL_HEIGHT + 2
        self._box(log_ox, log_oy, log_w, log_h, title='Log')
        self._render_log(engine, log_ox + 1, log_oy + 1, log_w - 2, log_h - 2)

        # ── Fill the gap between map and side panel borders ──
        # The outer box left a 1-cell column between map panel right border
        # and side panel left border — that's handled by the borders themselves.

        # Park cursor off-screen and flush everything in one write
        self._out_parts.append(self.term.move_xy(0, outer_h + 1))
        self._out_parts.append(self.term.normal)
        self._flush()

    # ── map rendering ────────────────────────────────────────────────────

    def _render_map(self, engine, fov_set, ox, oy):
        """Render every map cell exactly once."""
        player = engine.player
        enemies = engine.enemies
        items = engine.items
        game_map = engine.game_map

        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                tile = game_map[y][x]
                visible = (x, y) in fov_set
                explored = tile.explored

                # Flash override
                flash_bg = self._get_flash_bg(x, y)

                if visible:
                    tile.explored = True

                    # Check for entities / items at this position
                    entity = None
                    if player.x == x and player.y == y:
                        entity = 'player'
                    else:
                        entity = next((e for e in enemies if e.x == x and e.y == y), None)
                    item = next((i for i in items if i.x == x and i.y == y), None)

                    # Light falloff
                    dist = _distance(player.x, player.y, x, y)
                    falloff = max(0.0, 1.0 - dist / (FOV_RADIUS + 1))

                    if entity == 'player':
                        fg = FG_PLAYER
                        bg = flash_bg or BG_FLOOR_LIT
                        self._put(ox + x, oy + y, GLYPH_PLAYER, fg, bg)
                    elif entity is not None:
                        fg, glyph = self._entity_appearance(entity)
                        fg = _lerp_color(FG_TEXT_DIM, fg, falloff)
                        bg = flash_bg or BG_FLOOR_LIT
                        self._put(ox + x, oy + y, glyph, fg, bg)
                    elif item is not None:
                        fg, glyph = self._item_appearance(item)
                        fg = _lerp_color(FG_TEXT_DIM, fg, falloff)
                        bg = flash_bg or BG_FLOOR_LIT
                        self._put(ox + x, oy + y, glyph, fg, bg)
                    elif tile.is_stairs:
                        fg = FG_STAIRS
                        bg = flash_bg or BG_STAIRS_LIT
                        self._put(ox + x, oy + y, GLYPH_STAIRS, fg, bg)
                    elif tile.blocked:
                        fg = _lerp_color(FG_WALL_DIM, FG_WALL_LIT, falloff)
                        bg = flash_bg or _lerp_color(BG_WALL_DIM, BG_WALL_LIT, falloff)
                        self._put(ox + x, oy + y, tile.wall_glyph, fg, bg)
                    else:
                        fg = _lerp_color(FG_FLOOR_DIM, FG_FLOOR_LIT, falloff)
                        bg = flash_bg or _lerp_color(BG_FLOOR_DIM, BG_FLOOR_LIT, falloff)
                        self._put(ox + x, oy + y, GLYPH_FLOOR, fg, bg)
                elif explored:
                    if tile.is_stairs:
                        self._put(ox + x, oy + y, GLYPH_STAIRS, FG_STAIRS_DIM, BG_FLOOR_DIM)
                    elif tile.blocked:
                        self._put(ox + x, oy + y, tile.wall_glyph, FG_WALL_DIM, BG_WALL_DIM)
                    else:
                        self._put(ox + x, oy + y, GLYPH_FLOOR, FG_FLOOR_DIM, BG_FLOOR_DIM)
                else:
                    self._put(ox + x, oy + y, GLYPH_VOID, FG_VOID, BG_VOID)

    def _entity_appearance(self, entity):
        name = entity.name
        if 'Undergrad' in name:
            return FG_UNDERGRAD, GLYPH_UNDERGRAD
        elif 'Post-doc' in name:
            return FG_POSTDOC, GLYPH_POSTDOC
        elif 'Supervisor' in name:
            return FG_SUPERVISOR, GLYPH_SUPERVISOR
        return FG_TEXT, '?'

    def _item_appearance(self, item):
        if item.item_type == 'heal':
            return FG_ESPRESSO, GLYPH_ESPRESSO
        elif item.item_type == 'buff':
            return FG_GRANT, GLYPH_GRANT
        return FG_TEXT, '?'

    # ── side panel ───────────────────────────────────────────────────────

    def _render_side_panel(self, engine, fov_set, ox, oy, w, h):
        """Render side panel, writing every cell exactly once."""
        p = engine.player

        # Build lines as (text, fg) tuples — each will be padded to full width
        lines = []

        def add(text, fg=FG_TEXT):
            lines.append((text, fg))

        def add_blank():
            lines.append(('', FG_TEXT))

        # Player info line: "PhD Student" with glyph at right edge
        player_label = 'PhD Student'
        pad = w - len(player_label) - 1
        add(player_label + ' ' * max(0, pad) + GLYPH_PLAYER, FG_PLAYER)

        # Sanity label
        add('Sanity:', FG_TEXT)

        # HP bar (handled specially below)
        lines.append(None)  # placeholder for HP bar row

        # Stats
        iq_str = f'IQ: {p.power}'
        week_str = f'Week: {engine.week}'
        gap = w - len(iq_str) - len(week_str)
        add(iq_str + ' ' * max(1, gap) + week_str, FG_TEXT)

        add_blank()

        # Nearby header
        add('\u2500\u2500 Nearby \u2500\u2500', FG_BORDER)

        # Nearby entities
        nearby = []
        for e in engine.enemies:
            if (e.x, e.y) in fov_set:
                dist = abs(e.x - p.x) + abs(e.y - p.y)
                nearby.append((dist, e))
        nearby.sort(key=lambda t: t[0])

        if nearby:
            for dist, e in nearby[:4]:
                fg, glyph = self._entity_appearance(e)
                add(f'{glyph} {e.name}', fg)
        else:
            add('(none)', FG_TEXT_DIM)

        add_blank()

        # Legend header
        add('\u2500\u2500 Legend \u2500\u2500', FG_BORDER)

        legend = [
            (GLYPH_ESPRESSO, 'Espresso', FG_ESPRESSO),
            (GLYPH_GRANT, 'Grant', FG_GRANT),
            (GLYPH_STAIRS, 'Stairs (>)', FG_STAIRS),
        ]
        for glyph, label, fg in legend:
            add(f'{glyph} {label}', fg)

        add_blank()

        # Controls (place at bottom of panel)
        # Pad with blank lines until we reach the bottom
        controls = [
            ('WASD:Move >:Stairs', FG_TEXT_DIM),
            ('Q:Quit', FG_TEXT_DIM),
        ]
        # Fill remaining space before controls
        remaining = h - len(lines) - len(controls)
        for _ in range(max(0, remaining)):
            add_blank()
        for text, fg in controls:
            add(text, fg)

        # Now render all lines, exactly one write per cell
        for row_idx in range(h):
            if row_idx < len(lines) and lines[row_idx] is None:
                # HP bar row — special handling
                self._draw_hp_bar(ox, oy + row_idx, p.hp, p.max_hp,
                                  bar_width=min(14, w - 7))
                # Clear any remaining cells after the HP bar
                bar_end = min(14, w - 7) + 8  # bar + stat text
                for j in range(bar_end, w):
                    self._put(ox + j, oy + row_idx, ' ', FG_TEXT_DIM, BG_PANEL)
            elif row_idx < len(lines):
                text, fg = lines[row_idx]
                # Write text + padding, one cell each
                for col in range(w):
                    if col < len(text):
                        self._put(ox + col, oy + row_idx, text[col], fg, BG_PANEL)
                    else:
                        self._put(ox + col, oy + row_idx, ' ', FG_TEXT_DIM, BG_PANEL)
            else:
                # Beyond content — blank row
                for col in range(w):
                    self._put(ox + col, oy + row_idx, ' ', FG_TEXT_DIM, BG_PANEL)

    # ── log panel ────────────────────────────────────────────────────────

    def _render_log(self, engine, ox, oy, w, h):
        """Render log panel, writing every cell exactly once."""
        messages = engine.messages
        visible = list(messages)[-VISIBLE_LOG_MESSAGES:]

        for row in range(h):
            if row < len(visible):
                text, color = visible[row]
                # Newest message brightest, older dimmer
                age = len(visible) - 1 - row
                if age == 0:
                    fg = color
                elif age == 1:
                    fg = _lerp_color(color, FG_TEXT_DIM, 0.3)
                else:
                    fg = _lerp_color(color, FG_TEXT_DIM, 0.6)

                for col in range(w):
                    if col < len(text):
                        self._put(ox + col, oy + row, text[col], fg, BG_PANEL)
                    else:
                        self._put(ox + col, oy + row, ' ', FG_TEXT_DIM, BG_PANEL)
            else:
                for col in range(w):
                    self._put(ox + col, oy + row, ' ', FG_TEXT_DIM, BG_PANEL)

    # ── screen management ────────────────────────────────────────────────

    def clear(self):
        """Full clear and reset buffer."""
        sys.stdout.write(self.term.home + self.term.clear)
        sys.stdout.flush()
        self.prev_buffer.clear()
        self._needs_full_paint = True

    def enter_fullscreen(self):
        sys.stdout.write(self.term.enter_fullscreen + self.term.hide_cursor)
        sys.stdout.flush()
        self.clear()

    def exit_fullscreen(self):
        sys.stdout.write(self.term.normal_cursor + self.term.exit_fullscreen + self.term.normal)
        sys.stdout.flush()

    def get_key(self, timeout=None):
        """Get a keypress. Returns blessed Keystroke or empty string on timeout."""
        if timeout is not None:
            return self.term.inkey(timeout=timeout)
        return self.term.inkey()
