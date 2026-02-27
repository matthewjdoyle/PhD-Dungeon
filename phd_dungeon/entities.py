import random
from .constants import MAP_WIDTH, MAP_HEIGHT

class Entity:
    def __init__(self, x, y, char, color, name, hp=10, power=2):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.power = power
        # For autonomous movement
        self.wander_timer = 0
        self.last_dir = (0, 0)

    def move(self, dx, dy, game_map, enemies):
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT:
            if not game_map[new_y][new_x].blocked:
                # Check for other enemies to avoid stacking
                if not any([e for e in enemies if e != self and e.x == new_x and e.y == new_y]):
                    self.x = new_x
                    self.y = new_y
                    return True
        return False

    def act(self, player, game_map, enemies):
        """NPC specific action/AI logic"""
        dist = abs(player.x - self.x) + abs(player.y - self.y)
        detection_range = 8 if self.name == "The Supervisor" else 5
        
        if dist <= detection_range:
            # CHASE PLAYER
            edx = 1 if player.x > self.x else -1 if player.x < self.x else 0
            edy = 1 if player.y > self.y else -1 if player.y < self.y else 0
            
            if self.x + edx == player.x and self.y + edy == player.y:
                # 15% chance to miss
                if random.randint(0, 100) < 15:
                    return {"type": "miss"}
                
                # RNG Damage: 20% to 120% of power
                base_damage = self.power
                actual_damage = random.randint(int(base_damage * 0.2), int(base_damage * 1.2))
                return {"type": "attack", "damage": actual_damage}
            else:
                self.move(edx, edy, game_map, enemies)
        else:
            # AUTONOMOUS WANDER/PATROL
            if self.name == "Lost Undergrad":
                if random.randint(0, 100) < 30:
                    rdx, rdy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                    self.move(rdx, rdy, game_map, enemies)
            elif self.name == "Burned-out Post-doc":
                if self.wander_timer <= 0:
                    self.last_dir = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                    self.wander_timer = random.randint(2, 5)
                
                if not self.move(self.last_dir[0], self.last_dir[1], game_map, enemies):
                    self.wander_timer = 0
                else:
                    self.wander_timer -= 1
            elif self.name == "The Supervisor":
                if random.randint(0, 100) < 20:
                    rdx, rdy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                    self.move(rdx, rdy, game_map, enemies)
        return None
