import numpy as np
from .tile import Tile
from . import tile_types


class GameMap:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

        self.tiles = self.initialize_tiles()
        self.visible = np.full((self.width, self.height), fill_value=False, order="F")
        self.explored = np.full((self.width, self.height), fill_value=False, order="F")

    def initialize_tiles(self):
        return np.full((self.width, self.height), fill_value=tile_types.wall, order="F")

    def is_walkable(self, x: int, y: int) -> bool:
        return self.tiles[x][y].walkable

    def render(self, console):
        for x in range(self.width):
            for y in range(self.height):
                if self.visible[x, y]:
                    console.bg[x, y] = self.tiles[x, y].light
                elif self.explored[x, y]:
                    console.bg[x, y] = self.tiles[x, y].dark
