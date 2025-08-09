from .stats import Stats

class Entity:
    def __init__(self, x: int, y: int, char: str, color: tuple[int, int, int], name: str):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.stats = Stats()
        self.inventory = []
        self.effects = []  # For things like "can_walk_on_water"

    def move(self, dx: int, dy: int):
        self.x += dx
        self.y += dy

    def can_walk_on(self, tile_type: str) -> bool:
        if tile_type == 'water':
            return 'water_walking' in self.effects
        return True

class Item(Entity):
    def __init__(
        self,
        x: int,
        y: int,
        char: str,
        color: tuple[int, int, int],
        name: str,
        description: str,
        stat_modifiers: dict,
        effects: list[str] = None
    ):
        super().__init__(x, y, char, color, name)
        self.description = description
        self.stat_modifiers = stat_modifiers  # {'hp': 10, 'atk': 2, etc}
        self.effects = effects or []

    def apply_to(self, entity: Entity):
        """Apply item effects to an entity."""
        for stat, value in self.stat_modifiers.items():
            if hasattr(entity.stats, stat):
                setattr(entity.stats, stat, getattr(entity.stats, stat) + value)
        entity.effects.extend(self.effects)
