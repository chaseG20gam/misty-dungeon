from typing import Tuple

class Tile:
    def __init__(
        self,
        walkable: bool,
        transparent: bool,
        dark: Tuple[int, int, int],
        light: Tuple[int, int, int],
        name_id: str
    ):
        self.walkable = walkable
        self.transparent = transparent
        self.dark = dark
        self.light = light
        self.name_id = name_id
        self.explored = False  # for fog of war
