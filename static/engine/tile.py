from typing import Tuple

class Tile:
    def __init__(
        self,
        walkable: bool,
        transparent: bool,
        dark: Tuple[int, int, int],
        light: Tuple[int, int, int],
    ):
        self.walkable = walkable
        self.transparent = transparent
        self.dark = dark
        self.light = light
        self.explored = False  # for fog of war
