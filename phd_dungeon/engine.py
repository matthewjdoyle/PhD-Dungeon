import random
import time
from collections import deque
from .constants import *
from .map_gen import make_map
from .entities import Entity
from .items import Item
from .fov import compute_fov
from .renderer import Renderer
from .ui import show_title_screen, show_death_screen, show_level_transition


class GameEngine:
    def __init__(self):
        self.week = 1
        self.player = Entity(0, 0, '@', COLOR_YELLOW, 'PhD Student', hp=50, power=8)
        self.messages = deque(maxlen=MAX_LOG_MESSAGES)
        self.messages.append(("Welcome to the PhD Dungeon. The research never ends.", FG_MSG_EVENT))
        self.renderer = Renderer()
        self.new_level(first=True)

    def new_level(self, first=False):
        self.game_map, self.rooms, p_x, p_y = make_map(self.week)
        self.player.x, self.player.y = p_x, p_y
        self.enemies = []
        self.items = []

        for room in self.rooms[1:]:
            num_enemies = random.randint(0, MAX_ENEMIES_PER_ROOM)
            for i in range(num_enemies):
                x = random.randint(room.x1 + 1, room.x2 - 1)
                y = random.randint(room.y1 + 1, room.y2 - 1)
                if not any(e.x == x and e.y == y for e in self.enemies):
                    roll = random.randint(0, 100)
                    if roll < 60:
                        enemy = Entity(x, y, 'u', COLOR_GREEN, 'Lost Undergrad',
                                       hp=5 + self.week * 2, power=1 + self.week // 3)
                    elif roll < 90:
                        enemy = Entity(x, y, 'D', COLOR_BLUE, 'Burned-out Post-doc',
                                       hp=15 + self.week * 3, power=3 + self.week // 2)
                    else:
                        enemy = Entity(x, y, 'S', COLOR_RED, 'The Supervisor',
                                       hp=30 + self.week * 5, power=5 + self.week)
                    self.enemies.append(enemy)

            if random.randint(0, 100) < 40:
                ix = random.randint(room.x1 + 1, room.x2 - 1)
                iy = random.randint(room.y1 + 1, room.y2 - 1)
                if not any(e.x == ix and e.y == iy for e in self.enemies):
                    if random.randint(0, 1) == 0:
                        self.items.append(Item(ix, iy, '!', COLOR_GREEN, 'Espresso', 'heal'))
                    else:
                        self.items.append(Item(ix, iy, '$', COLOR_YELLOW, 'Research Grant', 'buff'))

    def add_message(self, text, color=FG_MSG_DEFAULT):
        self.messages.append((text, color))

    def handle_events(self):
        if random.randint(0, 100) < 2:
            event_roll = random.randint(0, 3)
            if event_roll == 0:
                loss = 5 + self.week
                self.player.hp -= loss
                self.add_message(f"EVENT: Reviewer #2 rejected your paper! -{loss} Sanity!", FG_MSG_DAMAGE_TAKEN)
            elif event_roll == 1:
                self.player.hp = min(self.player.hp + 10, self.player.max_hp)
                self.add_message("EVENT: Free Pizza in the breakroom! +10 Sanity!", FG_MSG_ITEM)
            elif event_roll == 2:
                self.player.power += 1
                self.add_message("EVENT: You found a working pipette! +1 IQ!", FG_MSG_EVENT)
            else:
                self.add_message("EVENT: The lab is unusually quiet today.", FG_MSG_EVENT)

    def run(self):
        r = self.renderer

        try:
            r.enter_fullscreen()

            with r.term.cbreak():
                show_title_screen(r)
                r.clear()

                while True:
                    # Compute FOV
                    fov_set = compute_fov(self.game_map, self.player.x, self.player.y)

                    # Render
                    r.render_game(self, fov_set)

                    # Check death
                    if self.player.hp <= 0:
                        time.sleep(0.3)
                        choice = show_death_screen(r, self)
                        if choice == 'retry':
                            self._reset()
                            r.clear()
                            continue
                        else:
                            break

                    # Input -- with timeout for animation
                    key = r.get_key(timeout=0.5)

                    # Tick visual events
                    r.tick_events()

                    if not key:
                        continue  # timeout, just re-render for animations

                    char = key.lower() if hasattr(key, 'lower') else str(key).lower()

                    if char == 'q':
                        break

                    if char == '>' and self.game_map[self.player.y][self.player.x].is_stairs:
                        self.week += 1
                        self.player.hp = min(self.player.hp + 15, self.player.max_hp)
                        show_level_transition(r, self.week)
                        self.new_level()
                        self.add_message(f"Starting Research Week {self.week}. Check your inbox.", FG_MSG_EVENT)
                        r.clear()
                        continue

                    dx, dy = 0, 0
                    if char == 'w':
                        dy = -1
                    elif char == 's':
                        dy = 1
                    elif char == 'a':
                        dx = -1
                    elif char == 'd':
                        dx = 1

                    if dx != 0 or dy != 0:
                        target_x = self.player.x + dx
                        target_y = self.player.y + dy

                        target_enemy = next((e for e in self.enemies
                                             if e.x == target_x and e.y == target_y), None)
                        if target_enemy:
                            base_damage = self.player.power
                            actual_damage = random.randint(
                                int(base_damage * 0.2), int(base_damage * 1.2))

                            is_crit = random.randint(0, 100) < 10
                            if is_crit:
                                actual_damage *= 2
                                self.add_message(
                                    f"CRITICAL INSIGHT! You stun {target_enemy.name} for {actual_damage}!",
                                    FG_MSG_DAMAGE_DEALT)
                                r.add_event('crit', target_enemy.x, target_enemy.y, frames=2)
                            else:
                                self.add_message(
                                    f"You explain physics to {target_enemy.name} for {actual_damage} dmg!",
                                    FG_MSG_DAMAGE_DEALT)
                                r.add_event('hit', target_enemy.x, target_enemy.y, frames=1)

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
                                self.add_message(random.choice(phrases), FG_MSG_DAMAGE_DEALT)
                                self.enemies.remove(target_enemy)
                        else:
                            if 0 <= target_x < MAP_WIDTH and 0 <= target_y < MAP_HEIGHT:
                                if not self.game_map[target_y][target_x].blocked:
                                    self.player.x, self.player.y = target_x, target_y

                                    target_item = next(
                                        (i for i in self.items
                                         if i.x == self.player.x and i.y == self.player.y), None)
                                    if target_item:
                                        msg = target_item.use(self.player)
                                        self.add_message(msg, FG_MSG_ITEM)
                                        self.items.remove(target_item)
                                else:
                                    self.add_message(
                                        "That is a wall. You cannot walk through walls yet.",
                                        FG_MSG_DEFAULT)

                        self.handle_events()

                        # Enemy turn
                        for enemy in self.enemies:
                            result = enemy.act(self.player, self.game_map, self.enemies)
                            if result:
                                if result["type"] == "attack":
                                    damage = result["damage"]
                                    self.player.hp -= damage
                                    r.add_event('player_hit', self.player.x, self.player.y, frames=1)
                                    if enemy.name == "Lost Undergrad":
                                        self.add_message(
                                            f"Undergrad asks a dumb question! -{damage} Sanity!",
                                            FG_MSG_DAMAGE_TAKEN)
                                    elif enemy.name == "Burned-out Post-doc":
                                        self.add_message(
                                            f"Post-doc talks about job market! -{damage} Sanity!",
                                            FG_MSG_DAMAGE_TAKEN)
                                    else:
                                        self.add_message(
                                            f"Supervisor asks for results! -{damage} Sanity!",
                                            FG_MSG_DAMAGE_TAKEN)
                                elif result["type"] == "miss":
                                    self.add_message(
                                        f"You dodged {enemy.name}'s argument!",
                                        FG_MSG_EVENT)

        finally:
            r.exit_fullscreen()

    def _reset(self):
        """Reset game state for retry."""
        self.week = 1
        self.player = Entity(0, 0, '@', COLOR_YELLOW, 'PhD Student', hp=50, power=8)
        self.messages.clear()
        self.messages.append(("Welcome to the PhD Dungeon. The research never ends.", FG_MSG_EVENT))
        self.renderer.visual_events.clear()
        self.new_level(first=True)
