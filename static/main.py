import tcod

from engine.entity import Entity
from engine import game_map
from engine.procgen import generate_dungeon

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAX_ROOMS = 30
ROOM_MIN_SIZE = 6
ROOM_MAX_SIZE = 10


def main():
    # generate dungeon and initial room list
    game_map, rooms = generate_dungeon(
        map_width=SCREEN_WIDTH,
        map_height=SCREEN_HEIGHT,
        max_rooms=MAX_ROOMS,
        room_min_size=ROOM_MIN_SIZE,
        room_max_size=ROOM_MAX_SIZE
    )
    
    # player in the first room's center
    player_x, player_y = rooms[0].center()
    player = Entity(player_x, player_y, "@", (255, 255, 255))
    entities = [player]

    tileset = tcod.tileset.load_tilesheet(
        "static/dejavu10x10_gs_tc.png",
        32,
        8,
        tcod.tileset.CHARMAP_TCOD,
    )

    with tcod.context.new_terminal(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        tileset=tileset,
        title="Misty Dungeon",
        vsync=True,
    ) as context:
        console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")

        while True:
            console.clear()

            # draw the map
            game_map.render(console)

            # draw entities
            for entity in entities:
                console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)

            context.present(console)

            # Handle input
            for event in tcod.event.wait():
                if event.type == "QUIT":
                    raise SystemExit()
                elif event.type == "KEYDOWN":
                    dx = dy = 0
                    if event.sym == tcod.event.K_UP:
                        dy = -1
                    elif event.sym == tcod.event.K_DOWN:
                        dy = 1
                    elif event.sym == tcod.event.K_LEFT:
                        dx = -1
                    elif event.sym == tcod.event.K_RIGHT:
                        dx = 1

                    # move only into walkable tiles
                    dest_x = player.x + dx
                    dest_y = player.y + dy

                    if game_map.is_walkable(dest_x, dest_y):
                        player.move(dx, dy)

if __name__ == "__main__":
    main()
