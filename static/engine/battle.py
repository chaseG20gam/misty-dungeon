import tcod

class BattleSystem:
    def __init__(self, player, enemy, context, screen_width, screen_height):
        self.player = player
        self.enemy = enemy
        self.context = context
        self.width = screen_width
        self.height = screen_height

    def start_battle(self):
        console = tcod.Console(self.width, self.height, order="F")
        
        while True:
            # render battle screen
            console.clear()
            self._draw_battle_screen(console)
            self.context.present(console)

            # handle player turn
            action = self._handle_player_turn(console)
            if action == "run":
                return False
            elif action == "attack":
                damage = 10 + self.player.stats.atk
                self.enemy.stats.hp -= damage
                if self.enemy.stats.hp <= 0:
                    self.player.stats.exp += 50
                    if self.player.stats.exp >= self.player.stats.next_level:
                        self.player.stats.level_up()
                    return True

            # enemy turn
            self.player.stats.hp -= 10
            if self.player.stats.hp <= 0:
                return False

    def _draw_battle_screen(self, console):
        # draw enemy stats
        console.print(2, 2, f"{self.enemy.name}")
        console.print(2, 3, f"HP: {self.enemy.stats.hp}")

        # draw player stats
        console.print(2, self.height-5, f"{self.player.name}")
        console.print(2, self.height-4, f"HP: {self.player.stats.hp}")

        # draw options
        console.print(2, self.height-2, "1) Attack  2) Run")

    def _handle_player_turn(self, console):
        while True:
            for event in tcod.event.wait():
                if event.type == "KEYDOWN":
                    if event.sym == tcod.event.K_1:
                        return "attack"
                    elif event.sym == tcod.event.K_2:
                        return "run"