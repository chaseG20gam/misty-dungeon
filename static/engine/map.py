import tcod

class Tile:
    def __init__(self, walkable, transparent):
        self.walkable = walkable
        self.transparent = transparent

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        return [[
            Tile(walkable=True, transparent=True) if x % 5 != 0 and y % 5 != 0
            else Tile(walkable=False, transparent=False)
            for x in range(self.width)
        ] for y in range(self.height)]

    def render(self, console):
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile.walkable:
                    console.print(x, y, ".", fg=(200, 200, 200))
                else:
                    console.print(x, y, "#", fg=(100, 100, 100))
