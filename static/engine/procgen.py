import random
from .game_map import GameMap
from .tile import Tile


class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return center_x, center_y

    def intersect(self, other):
        return (
            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )


def create_tunnel_x(game_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        game_map.tiles[x][y] = Tile(True, True)


def create_tunnel_y(game_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        game_map.tiles[x][y] = Tile(True, True)


def carve_room(game_map, room):
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            game_map.tiles[x][y] = Tile(True, True)


def generate_dungeon(map_width, map_height, max_rooms, room_min_size, room_max_size):
    game_map = GameMap(map_width, map_height)
    rooms = []

    for _ in range(max_rooms):
        w = random.randint(room_min_size, room_max_size)
        h = random.randint(room_min_size, room_max_size)
        x = random.randint(0, map_width - w - 1)
        y = random.randint(0, map_height - h - 1)

        new_room = Rect(x, y, w, h)

        if any(new_room.intersect(other_room) for other_room in rooms):
            continue

        carve_room(game_map, new_room)

        if rooms:
            prev_x, prev_y = rooms[-1].center()
            new_x, new_y = new_room.center()

            if random.random() < 0.5:
                create_tunnel_x(game_map, prev_x, new_x, prev_y)
                create_tunnel_y(game_map, prev_y, new_y, new_x)
            else:
                create_tunnel_y(game_map, prev_y, new_y, prev_x)
                create_tunnel_x(game_map, prev_x, new_x, new_y)

        rooms.append(new_room)

    return game_map, rooms
