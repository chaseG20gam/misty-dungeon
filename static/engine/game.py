from engine.map import GameMap

class Game:
    def __init__(self):
        self.map_width = 80
        self.map_height = 45
        self.game_map = GameMap(self.map_width, self.map_height)

    def render(self, console):
        self.game_map.render(console)

    def handle_events(self, event):
        # we'll handle input in future steps
        pass
