from .tile import Tile

floor = Tile(
    walkable=True,
    transparent=True,
    dark=(50, 50, 150),
    light=(200, 180, 50),
    name_id='floor'
)

wall = Tile(
    walkable=False,
    transparent=False,
    dark=(0, 0, 100),
    light=(130, 110, 50),
    name_id='wall'
)

stairs = Tile(
    walkable=True,
    transparent=True,
    dark=(0, 0, 150),
    light=(44, 44, 44),
    name_id='stairs'
)

water = Tile(
    walkable=False,
    transparent=True,
    dark=(0, 0, 80),
    light=(0, 0, 200),
    name_id='water'
)