class Stats:
    def __init__(self, level=1, hp=100, atk=10, defense=5):
        self.max_hp = hp
        self.hp = hp
        self.level = level
        self.atk = atk
        self.defense = defense
        self.exp = 0
        self.next_level = 100  # base exp needed for level 2

    def level_up(self):
        self.level += 1
        self.max_hp += 10
        self.hp = self.max_hp
        self.atk += 2
        self.defense += 1
        self.next_level *= 1.5  # increase exp needed for next level