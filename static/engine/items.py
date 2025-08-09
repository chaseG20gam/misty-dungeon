from .entity import Item

def create_water_sandals(x: int, y: int) -> Item:
    return Item(
        x=x,
        y=y,
        char="8",
        color=(0, 255, 255),
        name="Water Walking Sandals",
        description="Ancient sandals that let you walk on water.",
        stat_modifiers={'speed': 1},
        effects=['water_walking']
    )

def create_sword(x: int, y: int) -> Item:
    return Item(
        x=x,
        y=y,
        char="/",
        color=(255, 215, 0),
        name="Steel Sword",
        description="A well-crafted steel sword.",
        stat_modifiers={'atk': 5}
    )