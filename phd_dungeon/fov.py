"""Symmetric shadowcasting FOV algorithm (8 octants)."""

from .constants import MAP_WIDTH, MAP_HEIGHT, FOV_RADIUS


def compute_fov(game_map, px, py, radius=FOV_RADIUS):
    """Return set of (x, y) tiles visible from (px, py)."""
    visible = {(px, py)}

    for octant in range(8):
        _cast_light(game_map, px, py, radius, 1, 1.0, 0.0, octant, visible)

    return visible


# Octant multipliers: (xx, xy, yx, yy)
_MULT = [
    (1, 0, 0, 1),
    (0, 1, 1, 0),
    (0, -1, 1, 0),
    (-1, 0, 0, 1),
    (-1, 0, 0, -1),
    (0, -1, -1, 0),
    (0, 1, -1, 0),
    (1, 0, 0, -1),
]


def _cast_light(game_map, cx, cy, radius, row, start, end, octant, visible):
    if start < end:
        return

    xx, xy, yx, yy = _MULT[octant]
    new_start = start

    for j in range(row, radius + 1):
        blocked = False
        dx, dy = -j - 1, -j

        while dx <= 0:
            dx += 1
            mx = cx + dx * xx + dy * xy
            my = cy + dx * yx + dy * yy

            if not (0 <= mx < MAP_WIDTH and 0 <= my < MAP_HEIGHT):
                continue

            l_slope = (dx - 0.5) / (dy + 0.5)
            r_slope = (dx + 0.5) / (dy - 0.5)

            if start < r_slope:
                continue
            elif end > l_slope:
                break

            # Tile is within FOV radius (Euclidean)
            if dx * dx + dy * dy <= radius * radius:
                visible.add((mx, my))

            if blocked:
                if game_map[my][mx].blocked:
                    new_start = r_slope
                    continue
                else:
                    blocked = False
                    start = new_start
            else:
                if game_map[my][mx].blocked and j < radius:
                    blocked = True
                    _cast_light(game_map, cx, cy, radius, j + 1,
                                start, l_slope, octant, visible)
                    new_start = r_slope

        if blocked:
            break
