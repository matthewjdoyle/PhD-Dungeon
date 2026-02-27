import random
import os
import sys
import msvcrt
from .constants import *
from .map_gen import make_map
from .entities import Entity
from .items import Item

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_input():
    return msvcrt.getch()

class GameEngine:
    def __init__(self):
        self.week = 1
        self.player = Entity(0, 0, 'P', COLOR_YELLOW, 'PhD Student', hp=50, power=8)
        self.message = "Welcome to the PhD Dungeon. The research never ends."
        self.new_level()

    def new_level(self):
        self.game_map, self.rooms, p_x, p_y = make_map(self.week)
        self.player.x, self.player.y = p_x, p_y
        self.enemies = []
        self.items = []
        
        for room in self.rooms[1:]:
            # Place enemies
            num_enemies = random.randint(0, MAX_ENEMIES_PER_ROOM)
            for i in range(num_enemies):
                x = random.randint(room.x1 + 1, room.x2 - 1)
                y = random.randint(room.y1 + 1, room.y2 - 1)
                if not any([e.x == x and e.y == y for e in self.enemies]):
                    roll = random.randint(0, 100)
                    if roll < 60:
                        enemy = Entity(x, y, 'u', COLOR_GREEN, 'Lost Undergrad', hp=5+self.week*2, power=1+self.week//3)
                    elif roll < 90:
                        enemy = Entity(x, y, 'D', COLOR_BLUE, 'Burned-out Post-doc', hp=15+self.week*3, power=3+self.week//2)
                    else:
                        enemy = Entity(x, y, 'S', COLOR_RED, 'The Supervisor', hp=30+self.week*5, power=5+self.week)
                    self.enemies.append(enemy)
            
            # Place items
            if random.randint(0, 100) < 40:
                ix = random.randint(room.x1 + 1, room.x2 - 1)
                iy = random.randint(room.y1 + 1, room.y2 - 1)
                if not any([e.x == ix and e.y == iy for e in self.enemies]):
                    if random.randint(0, 1) == 0:
                        self.items.append(Item(ix, iy, 'e', COLOR_GREEN, 'Espresso', 'heal'))
                    else:
                        self.items.append(Item(ix, iy, 'g', COLOR_YELLOW, 'Research Grant', 'buff'))

    def render(self):
        clear_screen()
        print("\033[1m--- PhD DUNGEON ---\033[0m")
        for y in range(MAP_HEIGHT):
            line = ""
            for x in range(MAP_WIDTH):
                if self.player.x == x and self.player.y == y:
                    line += f"\033[{self.player.color}m{self.player.char}\033[0m"
                    continue
                enemy_here = next((e for e in self.enemies if e.x == x and e.y == y), None)
                if enemy_here:
                    line += f"\033[{enemy_here.color}m{enemy_here.char}\033[0m"
                    continue
                item_here = next((i for i in self.items if i.x == x and i.y == y), None)
                if item_here:
                    line += f"\033[{item_here.color}m{item_here.char}\033[0m"
                    continue
                if self.game_map[y][x].is_stairs:
                    line += f"\033[{COLOR_MAGENTA}mE\033[0m"
                    continue
                char = '#' if self.game_map[y][x].blocked else '.'
                line += f"\033[{COLOR_CYAN}m{char}\033[0m"
            print(line)

        print(f"\nWeek: {self.week} | Sanity: {self.player.hp}/{self.player.max_hp} | IQ: {self.player.power}")
        print(f"Log: {self.message}")

    def handle_events(self):
        if random.randint(0, 100) < 2:
            event_roll = random.randint(0, 3)
            if event_roll == 0:
                loss = 5 + self.week
                self.player.hp -= loss
                self.message = f"\033[31mEVENT: Reviewer #2 rejected your paper! -{loss} Sanity!\033[0m"
            elif event_roll == 1:
                self.player.hp = min(self.player.hp + 10, self.player.max_hp)
                self.message = "\033[32mEVENT: Free Pizza in the breakroom! +10 Sanity!\033[0m"
            elif event_roll == 2:
                self.player.power += 1
                self.message = "\033[33mEVENT: You found a working pipette! +1 IQ!\033[0m"
            else:
                self.message = "\033[36mEVENT: The lab is unusually quiet today.\033[0m"

    def run(self):
        while True:
            self.render()

            if self.player.hp <= 0:
                print("\033[31mYour Sanity hit zero. You have dropped out and now work in finance.\033[0m")
                break

            try:
                char = get_input().decode('utf-8').lower()
            except:
                continue

            if char == 'q':
                break
            
            if char == '>' and self.game_map[self.player.y][self.player.x].is_stairs:
                self.week += 1
                self.player.hp = min(self.player.hp + 15, self.player.max_hp)
                self.new_level()
                self.message = f"Starting Research Week {self.week}. Check your inbox."
                continue

            dx, dy = 0, 0
            if char == 'w': dy = -1
            elif char == 's': dy = 1
            elif char == 'a': dx = -1
            elif char == 'd': dx = 1

            if dx != 0 or dy != 0:
                target_x, target_y = self.player.x + dx, self.player.y + dy
                
                # Combat check
                target_enemy = next((e for e in self.enemies if e.x == target_x and e.y == target_y), None)
                if target_enemy:
                    # RNG Damage: 20% to 120% of power
                    base_damage = self.player.power
                    actual_damage = random.randint(int(base_damage * 0.2), int(base_damage * 1.2))
                    
                    # Critical Hit (10% chance)
                    is_crit = random.randint(0, 100) < 10
                    if is_crit:
                        actual_damage *= 2
                        self.message = f"CRITICAL INSIGHT! You stun {target_enemy.name} with a breakthrough for {actual_damage} dmg!"
                    else:
                        self.message = f"You explain physics to {target_enemy.name} for {actual_damage} dmg!"
                    
                    target_enemy.hp -= actual_damage
                    if target_enemy.hp <= 0:
                        phrases = [
                            f"The {target_enemy.name} was defeated by your logic!",
                            f"You out-argued the {target_enemy.name} during the seminar!",
                            f"The {target_enemy.name} retreated after seeing your data!",
                            f"You debunked the {target_enemy.name}'s counter-argument!",
                            f"The {target_enemy.name} left to rethink their entire life!",
                            f"The {target_enemy.name} was silenced by your peer-reviewed facts!"
                        ]
                        self.message = random.choice(phrases)
                        self.enemies.remove(target_enemy)
                else:
                    # Check walls
                    if 0 <= target_x < MAP_WIDTH and 0 <= target_y < MAP_HEIGHT:
                        if not self.game_map[target_y][target_x].blocked:
                            self.player.x, self.player.y = target_x, target_y
                            self.message = ""
                            
                            # Item check
                            target_item = next((i for i in self.items if i.x == self.player.x and i.y == self.player.y), None)
                            if target_item:
                                self.message = target_item.use(self.player)
                                self.items.remove(target_item)
                        else:
                            self.message = "That is a wall. You cannot walk through walls yet."
                    else:
                        self.message = "You cannot leave the lab. There is no escape."

                self.handle_events()

                # Enemy turn
                for enemy in self.enemies:
                    result = enemy.act(self.player, self.game_map, self.enemies)
                    if result:
                        if result["type"] == "attack":
                            damage = result["damage"]
                            self.player.hp -= damage
                            if enemy.name == "Lost Undergrad":
                                self.message += f" Undergrad asks a dumb question! -{damage} Sanity!"
                            elif enemy.name == "Burned-out Post-doc":
                                self.message += f" Post-doc talks about job market! -{damage} Sanity!"
                            else:
                                self.message += f" Supervisor asks for results! -{damage} Sanity!"
                        elif result["type"] == "miss":
                            self.message += f" You dodged {enemy.name}'s argument!"
