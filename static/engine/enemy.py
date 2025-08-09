from .entity import Entity
from .stats import Stats

class Enemy(Entity):
    def __init__(self, x: int, y: int, level: int):
        super().__init__(
            x=x,
            y=y,
            char="E",
            color=(255, 0, 0),
            name=f"Enemy Lvl {level}"
        )
        self.stats = Stats(
            level=level,
            hp=50 + (level * 10),
            atk=5 + level,
            defense=2 + level
        )

    def move_towards(self, target_x: int, target_y: int, game_map) -> tuple[int, int]:
        # move towards target while avoiding walls/water
        dx = target_x - self.x
        dy = target_y - self.y
        
        if abs(dx) > abs(dy):
            if dx > 0 and game_map.tiles[self.x + 1][self.y].walkable:
                return (1, 0)
            elif dx < 0 and game_map.tiles[self.x - 1][self.y].walkable:
                return (-1, 0)
        else:
            if dy > 0 and game_map.tiles[self.x][self.y + 1].walkable:
                return (0, 1)
            elif dy < 0 and game_map.tiles[self.x][self.y - 1].walkable:
                return (0, -1)
        return (0, 0)