from typing import Tuple

class Tile:
    def __init__(self, walkable: bool, transparent: bool):
        self.walkable = walkable
        self.transparent = transparent

        self.explored = False  # for FOV later
