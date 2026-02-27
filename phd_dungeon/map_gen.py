import random
from .constants import MAP_WIDTH, MAP_HEIGHT, ROOM_MIN_SIZE, ROOM_MAX_SIZE, MAX_ROOMS

class Tile:
    def __init__(self, blocked):
        self.blocked = blocked
        self.is_stairs = False

class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

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

    return game_map, rooms, player_start_x, player_start_y
