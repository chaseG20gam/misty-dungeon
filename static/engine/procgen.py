import random
import numpy as np
from .game_map import GameMap
from .tile import Tile
from . import tile_types


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


def is_tunnel_or_floor(tile):
    return tile.name_id in ('floor', 'tunnel')


def create_tunnel_x(game_map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        tile = game_map.tiles[x][y]
        # nly carve if not already a tunnel/floor, or if crossing
        if not is_tunnel_or_floor(tile) or (
            x > 0 and is_tunnel_or_floor(game_map.tiles[x-1][y]) and
            y > 0 and is_tunnel_or_floor(game_map.tiles[x][y-1])
        ):
            game_map.tiles[x][y] = Tile(True, True, dark=(60, 40, 20), light=(160, 110, 60), name_id='tunnel') # walkable tiles properties


def create_tunnel_y(game_map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        tile = game_map.tiles[x][y]
        if not is_tunnel_or_floor(tile) or (
            x > 0 and is_tunnel_or_floor(game_map.tiles[x-1][y]) and
            y > 0 and is_tunnel_or_floor(game_map.tiles[x][y-1])
        ):
            game_map.tiles[x][y] = Tile(True, True, dark=(60, 40, 20), light=(160, 110, 60), name_id='tunnel') # walkable tiles properties


def carve_room(game_map, room):
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            game_map.tiles[x][y] = Tile(True, True, dark=(60, 40, 20), light=(160, 110, 60), name_id='floor') # walkable tiles properties

def entrances_of_room(game_map, room):
    entrances = []
    for x in range(room.x1+1, room.x2-1):
        for y in [room.y1+1, room.y2-2]:
            if game_map.tiles[x][y].name_id == 'floor':
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if game_map.tiles[nx][ny].name_id == 'tunnel':
                        entrances.append((x, y))
    for y in range(room.y1+1, room.y2-1):
        for x in [room.x1+1, room.x2-2]:
            if game_map.tiles[x][y].name_id == 'floor':
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if game_map.tiles[nx][ny].name_id == 'tunnel':
                        entrances.append((x, y))
    return entrances

def is_room_connected(game_map, entrances):
    if not entrances:
        return True
    visited = set()
    stack = [entrances[0]]
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if (nx, ny) in entrances and (nx, ny) not in visited:
                stack.append((nx, ny))
            elif game_map.tiles[nx][ny].name_id == 'floor' and (nx, ny) not in visited:
                stack.append((nx, ny))
    return all(e in visited for e in entrances)

def add_water_pond(game_map, room, max_pond_size=12):
    # start pond 
    edge_choices = []
    # collect possible starting points for ponds to generate
    for x in range(room.x1, room.x2):
        edge_choices.append((x, room.y1))
        edge_choices.append((x, room.y2 - 1))
    for y in range(room.y1, room.y2):
        edge_choices.append((room.x1, y))
        edge_choices.append((room.x2 - 1, y))
    start_x, start_y = random.choice(edge_choices)
    pond_tiles = set()
    pond_tiles.add((start_x, start_y))

    # random walk to grow the pond
    for _ in range(random.randint(max_pond_size // 2, max_pond_size)):
        x, y = random.choice(list(pond_tiles))
        for _ in range(random.randint(1, 3)):
            dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
            nx, ny = x + dx, y + dy
            if 0 < nx < game_map.width-1 and 0 < ny < game_map.height-1:
                pond_tiles.add((nx, ny))

    # place water tiles 
    entrances = entrances_of_room(game_map, room)
    # save original tiles
    original_tiles = {(x, y): game_map.tiles[x][y] for x, y in pond_tiles}
    # place water (but not on stairs)
    for x, y in pond_tiles:
        if game_map.tiles[x][y].name_id != 'stairs':
            game_map.tiles[x][y] = Tile(
                walkable=False,
                transparent=True,
                dark=(80, 120, 200),
                light=(120, 180, 255),
                name_id='water'
            )
    # check connectivity
    if not is_room_connected(game_map, entrances):
        # revert pond
        for (x, y), tile in original_tiles.items():
            game_map.tiles[x][y] = tile


def add_water_pond_anywhere(game_map, max_pond_size=20, attempts=3):
    for _ in range(attempts):
        # pick a random tunnel or wall edge location
        x = random.randint(1, game_map.width - 2)
        y = random.randint(1, game_map.height - 2)
        # only start if it's a tunnel or wall (not floor)
        if game_map.tiles[x][y].name_id in ('tunnel',): 
            pond_tiles = set()
            pond_tiles.add((x, y))
            for _ in range(random.randint(max_pond_size // 2, max_pond_size)):
                px, py = random.choice(list(pond_tiles))
                for _ in range(random.randint(1, 3)):
                    dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                    nx, ny = px + dx, py + dy
                    if 0 < nx < game_map.width-1 and 0 < ny < game_map.height-1:
                        pond_tiles.add((nx, ny))
            for px, py in pond_tiles:
                game_map.tiles[px][py] = Tile(
                    walkable=False,
                    transparent=True,
                    dark=(80, 120, 200),
                    light=(120, 180, 255),
                    name_id='water'
                )


def add_water_pond_on_tunnel_edges(game_map, max_pond_size=20, attempts=8):
    width, height = game_map.width, game_map.height
    tunnel_edge_candidates = []

    # find wall tiles adjacent to tunnels (tunnel edges)
    for x in range(1, width-1):
        for y in range(1, height-1):
            if game_map.tiles[x][y].name_id not in ('wall',):  # only consider wall tiles, ponds grow towards the wall, not the floor
                continue
            # check if adjacent to tunnel
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if game_map.tiles[nx][ny].name_id in ('tunnel',):
                    tunnel_edge_candidates.append((x, y))
                    break

    for _ in range(min(attempts, len(tunnel_edge_candidates))):
        if not tunnel_edge_candidates:
            break
        start = random.choice(tunnel_edge_candidates)
        tunnel_edge_candidates.remove(start)
        pond_tiles = set()
        pond_tiles.add(start)
        for _ in range(random.randint(max_pond_size // 2, max_pond_size)):
            x, y = random.choice(list(pond_tiles))
            for _ in range(random.randint(1, 3)):
                dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
                nx, ny = x + dx, y + dy
                # only grow into wall tiles
                if 0 < nx < width-1 and 0 < ny < height-1:
                    if game_map.tiles[nx][ny].name_id == 'wall':
                        pond_tiles.add((nx, ny))
        for x, y in pond_tiles:
            game_map.tiles[x][y] = Tile(
                walkable=False,
                transparent=True,
                dark=(80, 120, 200),
                light=(120, 180, 255),
                name_id='water'
            )


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

        if random.random() < 0.5:  # chance to add water pond
            add_water_pond(game_map, new_room, max_pond_size=25)

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

    # find all floor tiles
    floor_tiles = [(x, y) for x in range(game_map.width) for y in range(game_map.height)
                   if game_map.tiles[x][y].name_id == 'floor']
    stairs_x, stairs_y = random.choice(floor_tiles)
    game_map.tiles[stairs_x][stairs_y] = tile_types.stairs

    # add ponds in tunnels and at edges
    # add_water_pond_anywhere(game_map, max_pond_size=20, attempts=5)
    add_water_pond_on_tunnel_edges(game_map, max_pond_size=25, attempts=10)

    return game_map, rooms
