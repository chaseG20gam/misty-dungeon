from .tile import Tile

floor = Tile(
    walkable=True,
    transparent=True,
    dark=(50, 50, 150),
    light=(200, 180, 50),
)

wall = Tile(
    walkable=False,
    transparent=False,
    dark=(0, 0, 100),
    light=(130, 110, 50),
)

stairs = Tile(
    walkable=True,
    transparent=True,
    dark=(0, 0, 150),
    light=(50, 50, 250),
)