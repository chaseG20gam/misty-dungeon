import tcod
import numpy as np

from engine.entity import Entity
from engine import game_map
from engine.procgen import *
from tcod.map import compute_fov

# screen constants
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 60

# floor atributes
panel_width = SCREEN_WIDTH

# window constants
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

# room constants
MAX_ROOMS = 30
ROOM_MIN_SIZE = 6
ROOM_MAX_SIZE = 10

# map constants
MAP_HEIGHT = SCREEN_HEIGHT - PANEL_HEIGHT
MAP_WIDTH = SCREEN_WIDTH

#fov constants
FOV_RADIUS = 8

def next_floor_popup (context, console, question, options=('yes', 'no')):
    width = max(len(question), max(len(opt) for opt in options)) + 4
    height = len(options) + 4
    x = (SCREEN_WIDTH - width) // 2
    y = (SCREEN_HEIGHT - height) // 2

    # new temporary console for the pop up
    panel = tcod.Console(width, height, order='F')
    panel.clear(bg=(0, 0, 0))
    panel.print_box(0, 0, width, 1, question, fg=(255, 255, 255), bg=(50, 50, 50), alignment=tcod.CENTER)

    selected = 0
    while True:
        # print options
        for i, opt in enumerate(options):
            fg=(255, 255, 0) if i == selected else (200, 200, 200)
            panel.print(2, 2 + i, opt, fg=fg)

        panel.blit(console, x, y)
        context.present(console)

        # input
        for event in tcod.event.wait():
            if event.type == 'QUIT':
                raise SystemExit()
            elif event.type == 'KEYDOWN':
                if event.sym in (tcod.event.K_UP, tcod.event. K_w):
                    selected = (selected - 1) % len(options)
                elif event.sym in (tcod.event.K_DOWN, tcod.event. K_s):
                    selected = (selected - 1) % len(options)
                elif event.sym in (tcod.event.K_RETURN, tcod.event. K_KP_ENTER):
                    return options[selected]
                elif event.sym == tcod.event.K_ESCAPE:
                    return 'no'

def main():
    # define current floor
    current_floor = 1

    # generate dungeon and room list
    dungeon, rooms = generate_dungeon(
        map_width=SCREEN_WIDTH,
        map_height=MAP_HEIGHT,
        max_rooms=MAX_ROOMS,
        room_min_size=ROOM_MIN_SIZE,
        room_max_size=ROOM_MAX_SIZE
    )

    # place player at center of first room
    player_x, player_y = rooms[0].center()
    player = Entity(player_x, player_y, "@", (255, 255, 0)) # adjust player color
    entities = [player]

    tileset = tcod.tileset.load_tilesheet(
        "../dejavu10x10_gs_tc.png",  # adjust this path if needed
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
    ) as context: # add windows here
        console = tcod.Console(SCREEN_WIDTH, SCREEN_HEIGHT, order="F")
        panel = tcod.Console(panel_width, PANEL_HEIGHT, order="F")

        while True:
            # compute fvo before rendering
            dungeon.visible[:] = compute_fov(
                transparency=np.vectorize(lambda t: t.transparent)(dungeon.tiles),
                pov=(player.x, player.y),
                radius=FOV_RADIUS,
                light_walls=True,
            )
            console.clear() # don't leave trail

            # render map based on FOV
            dungeon.render(console)

            # draw visible entities
            for entity in entities:
                if dungeon.visible[entity.x, entity.y]:
                    console.print(x=entity.x, y=entity.y, string=entity.char, fg=entity.color)

            dungeon.explored |= dungeon.visible  # mark seen tiles

            panel.clear()
            panel.print(1, 1, f"floor: {current_floor}", fg=(255, 255, 255))
            panel.print(1, 3, f"HP: 100/100", fg=(255, 0, 0))
            panel.print(1, 5, f"placeholder", fg=(200, 200, 200))

            panel.blit(console, 0, PANEL_Y)

            context.present(console)

            # handle input
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

                    if dungeon.is_walkable(dest_x, dest_y):
                        player.move(dx, dy)
            
            if dungeon.tiles[player.x][player.y].name_id == 'stairs':
                choice = next_floor_popup(context, console, 'Proceed to next flor?')
                if choice == 'yes':
                    current_floor += 1
                    dungeon, rooms = generate_dungeon(
                        map_width=SCREEN_WIDTH,
                        map_height=SCREEN_HEIGHT,
                        max_rooms=MAX_ROOMS,
                        room_min_size=ROOM_MIN_SIZE,
                        room_max_size=ROOM_MAX_SIZE
                    )
                    nx, ny = rooms[0].center()
                    player.x, player.y = nx, ny
                    entities = [player]


if __name__ == "__main__":
    main()
