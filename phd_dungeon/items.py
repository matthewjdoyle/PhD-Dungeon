import random

class Item:
    def __init__(self, x, y, char, color, name, item_type):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.item_type = item_type # 'heal' or 'buff'

    def use(self, player):
        if self.item_type == 'heal':
            player.hp = min(player.hp + 10, player.max_hp)
            phrases = [
                f"You drink {self.name}. +10 Sanity!",
                f"A shot of {self.name} keeps the burnout away! +10 Sanity.",
                f"The {self.name} kicks in. Your brain starts working again! +10 Sanity.",
                f"Bitter {self.name}, just like your dissertation. +10 Sanity.",
                f"Liquid focus! You feel much better after that {self.name}. +10 Sanity."
            ]
            return random.choice(phrases)
        elif self.item_type == 'buff':
            player.power += 3
            phrases = [
                f"You received a {self.name}! +3 IQ!",
                f"The {self.name} was approved! You can finally afford a new laser. +3 IQ!",
                f"Funding acquired! Your stress decreases as your IQ increases. +3 IQ!",
                f"A {self.name} falls from the sky! Science is easier when you're rich. +3 IQ!",
                f"Your {self.name} application was a success! +3 IQ!"
            ]
            return random.choice(phrases)
        return ""
