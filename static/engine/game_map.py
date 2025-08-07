import numpy as np
from .tile import Tile


class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        return np.full((self.width, self.height), fill_value=Tile(False, False), order="F")

    def is_walkable(self, x: int, y: int) -> bool:
        return self.tiles[x][y].walkable

    def render(self, console):
        for x in range(self.width):
            for y in range(self.height):
                tile = self.tiles[x][y]
                if tile.walkable:
                    console.print(x, y, ".", fg=(50, 50, 150))
                else:
                    console.print(x, y, "#", fg=(100, 100, 100))
