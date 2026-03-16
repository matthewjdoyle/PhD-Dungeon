import random
from .constants import MAP_WIDTH, MAP_HEIGHT, ROOM_MIN_SIZE, ROOM_MAX_SIZE, MAX_ROOMS, WALL_GLYPHS


class Tile:
    __slots__ = ('blocked', 'is_stairs', 'explored', 'wall_glyph')

    def __init__(self, blocked):
        self.blocked = blocked
        self.is_stairs = False
        self.explored = False
        self.wall_glyph = WALL_GLYPHS[0]  # default solid block


class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        return ((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def intersect(self, other):
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


def create_room(game_map, room):
    for y in range(room.y1 + 1, room.y2):
        for x in range(room.x1 + 1, room.x2):
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                game_map[y][x].blocked = False


def create_h_tunnel(game_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            game_map[y][x].blocked = False


def create_v_tunnel(game_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
            game_map[y][x].blocked = False


def compute_wall_glyphs(game_map):
    """Post-process: assign box-drawing glyphs to wall tiles based on neighbors."""
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            if not game_map[y][x].blocked:
                continue
            bitmask = 0
            # N
            if y > 0 and game_map[y - 1][x].blocked:
                bitmask |= 1
            # E
            if x < MAP_WIDTH - 1 and game_map[y][x + 1].blocked:
                bitmask |= 2
            # S
            if y < MAP_HEIGHT - 1 and game_map[y + 1][x].blocked:
                bitmask |= 4
            # W
            if x > 0 and game_map[y][x - 1].blocked:
                bitmask |= 8
            game_map[y][x].wall_glyph = WALL_GLYPHS[bitmask]


def make_map(week):
    game_map = [[Tile(True) for x in range(MAP_WIDTH)] for y in range(MAP_HEIGHT)]
    rooms = []
    player_start_x, player_start_y = 0, 0

    for r in range(MAX_ROOMS):
        w = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = random.randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = random.randint(0, MAP_WIDTH - w - 1)
        y = random.randint(0, MAP_HEIGHT - h - 1)

        new_room = Rect(x, y, w, h)
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            create_room(game_map, new_room)
            (new_x, new_y) = new_room.center()

            if len(rooms) == 0:
                player_start_x, player_start_y = new_x, new_y
            else:
                (prev_x, prev_y) = rooms[-1].center()
                if random.randint(0, 1) == 1:
                    create_h_tunnel(game_map, prev_x, new_x, prev_y)
                    create_v_tunnel(game_map, prev_y, new_y, new_x)
                else:
                    create_v_tunnel(game_map, prev_y, new_y, prev_x)
                    create_h_tunnel(game_map, prev_x, new_x, new_y)

            rooms.append(new_room)

    stairs_x, stairs_y = rooms[-1].center()
    game_map[stairs_y][stairs_x].is_stairs = True

    compute_wall_glyphs(game_map)

    return game_map, rooms, player_start_x, player_start_y
