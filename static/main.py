import tcod
import numpy as np

from engine.entity import Entity, Item
from engine import game_map
from engine.procgen import *
from engine.enemy import Enemy
from engine.battle import BattleSystem
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
ROOM_MAX_SIZE = 14

# map constants
MAP_HEIGHT = SCREEN_HEIGHT - PANEL_HEIGHT
MAP_WIDTH = SCREEN_WIDTH

#fov constants
FOV_RADIUS = 9

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

def item_pickup_popup(context, console, item):
    lines = [
        f"{item.name}",
        "─" * 20,
        f"{item.description}",
        "─" * 20,
        "Stats:",
    ]
    for stat, value in item.stat_modifiers.items():
        prefix = "+" if value > 0 else ""
        lines.append(f"{stat}: {prefix}{value}")
    if item.effects:
        lines.append("─" * 20)
        lines.append("Effects:")
        for effect in item.effects:
            lines.append(f"• {effect}")
    
    width = max(len(line) for line in lines) + 4
    height = len(lines) + 6
    x = (SCREEN_WIDTH - width) // 2
    y = (SCREEN_HEIGHT - height) // 2

    panel = tcod.Console(width, height, order='F')
    panel.clear(bg=(0, 0, 0))
    
    for i, line in enumerate(lines):
        panel.print(2, i + 1, line, fg=(255, 255, 255))
    
    panel.print(2, height - 3, "Pick up? (Y/N)", fg=(255, 255, 0))
    
    while True:
        panel.blit(console, x, y)
        context.present(console)
        
        for event in tcod.event.wait():
            if event.type == "KEYDOWN":
                if event.sym in (tcod.event.K_y, tcod.event.K_RETURN):
                    return True
                if event.sym in (tcod.event.K_n, tcod.event.K_ESCAPE):
                    return False

def main():
    # define current floor
    current_floor = 1
    picked_up_items = set()  # Track unique items picked up

    # generate dungeon and room list
    dungeon, rooms, items = generate_dungeon(  # Note: now receiving items
        map_width=SCREEN_WIDTH,
        map_height=MAP_HEIGHT,
        max_rooms=MAX_ROOMS,
        room_min_size=ROOM_MIN_SIZE,
        room_max_size=ROOM_MAX_SIZE
    )

    # place player at center of first room
    player_x, player_y = rooms[0].center()
    player = Entity(player_x, player_y, "@", (255, 255, 0), name='player') # adjust player color
    entities = [player] + items  # add items to entities list

    # Add enemy to first available room that's not player's room
    enemy_room = rooms[1]
    enemy_x, enemy_y = enemy_room.center()
    enemy = Enemy(enemy_x, enemy_y, current_floor)
    entities.append(enemy)

    tileset = tcod.tileset.load_tilesheet(
        "../dejavu16x16_gs_tc.png",  # adjust this path if needed
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

        prev_player_pos = (player.x, player.y) # track previous player position
        prev_item_check = None

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

            # update panel information
            panel.clear()
            y = 1
            panel.print(1, y, f"Floor: {current_floor}", fg=(255, 255, 255))
            y += 2
            panel.print(1, y, f"HP: {player.stats.hp}/{player.stats.max_hp}", fg=(255, 0, 0))
            y += 1
            panel.print(1, y, f"ATK: {player.stats.atk}", fg=(255, 215, 0))
            y += 1
            panel.print(1, y, f"DEF: {player.stats.defense}", fg=(0, 255, 0))
            y += 1
            
            # show special abilities
            if 'water_walking' in player.effects:
                panel.print(1, y, "Can walk on water", fg=(0, 255, 255))
            
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

                    if dx != 0 or dy != 0:  # only process movement if player actually moved
                        dest_x = player.x + dx
                        dest_y = player.y + dy

                        can_move = (
                            dungeon.is_walkable(dest_x, dest_y) or
                            (dungeon.tiles[dest_x][dest_y].name_id == 'water' and player.can_walk_on('water'))
                        )
                        
                        if can_move:
                            prev_player_pos = (player.x, player.y)
                            player.move(dx, dy)

                            # move enemy only after player has moved
                            for entity in entities:
                                if isinstance(entity, Enemy):
                                    dx, dy = entity.move_towards(player.x, player.y, dungeon)
                                    next_x = entity.x + dx
                                    next_y = entity.y + dy
                                    if (0 <= next_x < MAP_WIDTH and 
                                        0 <= next_y < MAP_HEIGHT and 
                                        dungeon.tiles[next_x][next_y].name_id not in ('water', 'wall')):
                                        entity.move(dx, dy)


            # check for items at player position
            current_pos = (player.x, player.y)
            for entity in entities[:]:
                if (isinstance(entity, Item) and 
                    entity.x == player.x and 
                    entity.y == player.y):
                
                    # only show popup if:
                    # - we just moved here OR
                    # - we ve never picked up this type of item
                    if current_pos != prev_item_check:
                        prev_item_check = current_pos
                        if item_pickup_popup(context, console, entity):
                            entity.apply_to(player)
                            picked_up_items.add(entity.name)  # track picked up item
                            entities.remove(entity)
                        else:
                            # only move back if we declined pickup
                            player.x, player.y = prev_player_pos
                            prev_item_check = None  # reset check to allow trying again

            # only show popup if player just moved onto stairs
            if (
                dungeon.tiles[player.x][player.y].name_id == 'stairs'
                and prev_player_pos != (player.x, player.y)
            ):
                choice = next_floor_popup(context, console, 'Proceed to next floor?')
                if choice == 'yes':
                    current_floor += 1
                    # update dungeon generation to consider picked up items
                    dungeon, rooms, new_items = generate_dungeon(
                        map_width=SCREEN_WIDTH,
                        map_height=MAP_HEIGHT,
                        max_rooms=MAX_ROOMS,
                        room_min_size=ROOM_MIN_SIZE,
                        room_max_size=ROOM_MAX_SIZE,
                        picked_up_items=picked_up_items  # pass tracked items
                    )
                    # place player in first room of new floor
                    nx, ny = rooms[0].center()
                    player.x, player.y = nx, ny
                    
                    # spawn new enemy in a room that's not the player's room
                    enemy_room = rooms[1]  # use second room
                    enemy_x, enemy_y = enemy_room.center()
                    enemy = Enemy(enemy_x, enemy_y, current_floor)  # enemy level matches floor
                    
                    # update entities list with new items and enemy
                    entities = [player] + new_items + [enemy]
                else:
                    # popup doesn't repeat, softlock fixed
                    prev_player_pos = (player.x, player.y)

            # after player moves, check for enemy collision
            for entity in entities[:]:
                if isinstance(entity, Enemy) and entity.x == player.x and entity.y == player.y:
                    battle = BattleSystem(player, entity, context, SCREEN_WIDTH, SCREEN_HEIGHT)
                    result = battle.start_battle()
                    # move player back and remove enemy in both cases (victory or run)
                    player.x, player.y = prev_player_pos
                    entities.remove(entity)
                    
                    if result:  # victory
                        # could add message or effects for victory here
                        pass
                    else:  # ran away or lost
                        # could add message for running away here
                        pass

            # move enemy after player's turn
            for entity in entities:
                if isinstance(entity, Enemy):
                    # enemy always moves, regardless of visibility
                    dx, dy = entity.move_towards(player.x, player.y, dungeon)
                    next_x = entity.x + dx
                    next_y = entity.y + dy
                    # check if next position is walkable (not water or wall)
                    if (0 <= next_x < MAP_WIDTH and 
                        0 <= next_y < MAP_HEIGHT and 
                        dungeon.tiles[next_x][next_y].name_id not in ('water', 'wall')):
                        entity.move(dx, dy)


if __name__ == "__main__":
    main()
