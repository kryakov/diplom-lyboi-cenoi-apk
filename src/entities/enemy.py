import math
from collections import deque

from src.entities.projectile import Projectile

# Спрайты, для которых нарисованы анимации (ключи вида <sprite>_<действие>_<сторона>_<кадр>).
ANIMATED_SPRITES = ("enemy_english_melee", "enemy_binary_melee", "enemy_formula_melee", "enemy_hse_bird")
DIRS = ["e", "se", "s", "sw", "w", "nw", "n", "ne"]
FRAME_COUNT = {"idle": 2, "walk": 4}
FRAME_RATE = {"idle": 2, "walk": 8}
DRAW_SIZE = 48              # размер картинки врага на экране (хитбокс SIZE не меняется)
FEET = 31 / 32              # низ ног в кадре (доля высоты картинки)
SHOT_FLASH_TIME = 0.1
BEAK_BASE = 24              # точки клюва в логе измерены для размера 24
# Кончик открытого клюва ворона относительно центра картинки (docs/ART_LOG.md, раздел 3.3).
BEAK = {"s": (0, 3), "se": (4, 2), "e": (9, -1), "ne": (8, -1),
        "n": (0, -10), "nw": (-8, -1), "w": (-9, -1), "sw": (-4, 2)}


def dir8(dx, dy):
    angle = math.degrees(math.atan2(dy, dx)) % 360
    return DIRS[int((angle + 22.5) // 45) % 8]


def direction(src, dst):
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    d = math.hypot(dx, dy)
    if d < 1e-6:
        return (1.0, 0.0), 0.0
    return (dx / d, dy / d), d


class Enemy:
    SIZE = 24
    STRIKE_TIME = 0.15
    REPATH_TIME = 0.3
    WAYPOINT_REACHED = 6

    def __init__(self, data, pos):
        self.id = data["id"]
        self.name = data["name"]
        self.kind = data["kind"]
        self.sprite = data["sprite"]
        self.max_hp = data["hp"]
        self.hp = data["hp"]
        self.speed = data["speed"]
        self.contact_damage = data["contact_damage"]
        self.attack = data.get("attack")
        # kind "ranged" (ворон ВШЭ): {"range", "windup", "cooldown", "projectile_speed", "damage"}
        self.shoot = data.get("shoot")
        self.shot_flash = 0.0
        self.x, self.y = float(pos[0]), float(pos[1])
        self.alive = True
        self.hurt_timer = 0.0
        self._projectiles = []
        self.state = "chase"
        self.timer = 0.0
        self.strike_dir = (1.0, 0.0)
        self.waypoint = None
        self.path_timer = 0.0
        self.facing = "s"
        self.anim = "walk"
        self.anim_time = 0.0

    @property
    def rect(self):
        h = self.SIZE / 2
        return (self.x - h, self.y - h, self.SIZE, self.SIZE)

    @property
    def center(self):
        return (self.x, self.y)

    def take_damage(self, n):
        if not self.alive:
            return
        self.hp -= n
        self.hurt_timer = 0.12
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def take_projectiles(self):
        out, self._projectiles = self._projectiles, []
        return out

    def attack_hitbox(self):
        if not self.alive or self.state != "strike":
            return None
        r = self.attack["range"]
        side = r + 12
        cx = self.x + self.strike_dir[0] * r / 2
        cy = self.y + self.strike_dir[1] * r / 2
        return ((cx - side / 2, cy - side / 2, side, side), self.attack["damage"])

    def _line_clear(self, room, src, dst):
        half = self.SIZE / 2
        steps = int(math.hypot(dst[0] - src[0], dst[1] - src[1]) // 10) + 1
        for i in range(1, steps + 1):
            t = i / steps
            x = src[0] + (dst[0] - src[0]) * t
            y = src[1] + (dst[1] - src[1]) * t
            if room.blocked((x - half, y - half, self.SIZE, self.SIZE)):
                return False
        return True

    def _find_waypoint(self, room, target):
        """Кратчайший путь по клеткам (BFS) в обход стен; возвращает ближайшую видимую точку пути."""
        tile = getattr(room, "tile", 30)
        width, height = getattr(room, "size_px", (960, 540))
        cols, rows = width // tile, height // tile
        half = self.SIZE / 2

        def free(cell):
            cx, cy = cell[0] * tile + tile / 2, cell[1] * tile + tile / 2
            return not room.blocked((cx - half, cy - half, self.SIZE, self.SIZE))

        start = (int(self.x // tile), int(self.y // tile))
        goal = (int(target[0] // tile), int(target[1] // tile))
        parent = {start: None}
        queue = deque([start])
        while queue and goal not in parent:
            cell = queue.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nxt = (cell[0] + dx, cell[1] + dy)
                if 0 <= nxt[0] < cols and 0 <= nxt[1] < rows and nxt not in parent and (nxt == goal or free(nxt)):
                    parent[nxt] = cell
                    queue.append(nxt)
        if goal not in parent:
            return None
        path = []
        cell = goal
        while cell is not None:
            path.append(cell)
            cell = parent[cell]
        path.reverse()
        points = [(c[0] * tile + tile / 2, c[1] * tile + tile / 2) for c in path[1:]]
        for point in reversed(points):
            if self._line_clear(room, self.center, point):
                return point
        return points[0] if points else None

    def _step_towards(self, dt, room, target, speed):
        if self._line_clear(room, self.center, target):
            dest = target
            self.waypoint = None
        else:
            self.path_timer -= dt
            if self.waypoint is None or self.path_timer <= 0:
                self.waypoint = self._find_waypoint(room, target)
                self.path_timer = self.REPATH_TIME
            dest = self.waypoint or target
        (ux, uy), dist = direction(self.center, dest)
        if self.waypoint is not None and dist < self.WAYPOINT_REACHED:
            self.waypoint = None
        h = self.SIZE / 2
        nx, ny = room.slide((self.x - h, self.y - h, self.SIZE, self.SIZE), ux * speed * dt, uy * speed * dt)
        self.x, self.y = nx + h, ny + h

    def update(self, dt, room, target):
        if not self.alive:
            return
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.shot_flash = max(0.0, self.shot_flash - dt)
        if self.attack is None:
            self._update_ranged(dt, room, target)
            return
        a = self.attack
        if self.state == "chase":
            dir_, dist = direction(self.center, target)
            if dist <= a["range"]:
                self.state, self.timer, self.strike_dir = "windup", a["windup"], dir_
            else:
                self._step_towards(dt, room, target, self.speed)
        elif self.state == "windup":
            self.timer -= dt
            if self.timer <= 0:
                self.state, self.timer = "strike", self.STRIKE_TIME
        elif self.state == "strike":
            self.timer -= dt
            if self.timer <= 0:
                self.state, self.timer = "cooldown", a["cooldown"]
        elif self.state == "cooldown":
            self.timer -= dt
            if self.timer <= 0:
                self.state = "chase"

        face = self.strike_dir if self.state in ("windup", "strike") else direction(self.center, target)[0]
        self.facing = dir8(*face)
        action = {"chase": "walk", "windup": "attack", "strike": "attack", "cooldown": "idle"}[self.state]
        if action != self.anim:
            self.anim = action
            self.anim_time = 0.0
        else:
            self.anim_time += dt

    def _update_ranged(self, dt, room, target):
        """Стрелок: идёт к герою, пока тот дальше range или за стеной; потом замах, одна пуля, пауза."""
        sh = self.shoot
        dir_, dist = direction(self.center, target)
        if self.state == "chase":
            if dist <= sh["range"] and self._line_clear(room, self.center, target):
                self.state, self.timer, self.strike_dir = "windup", sh["windup"], dir_
            else:
                self._step_towards(dt, room, target, self.speed)
        elif self.state == "windup":
            self.timer -= dt
            self.strike_dir = dir_
            if self.timer <= 0:
                self._fire(target)
                self.state, self.timer = "cooldown", sh["cooldown"]
        else:
            self.timer -= dt
            if self.timer <= 0:
                self.state = "chase"

        aiming = self.state == "windup" or self.shot_flash > 0
        self.facing = dir8(*(self.strike_dir if aiming else dir_))
        action = "walk" if self.state == "chase" else ("shoot" if aiming else "idle")
        if action != self.anim:
            self.anim = action
            self.anim_time = 0.0
        else:
            self.anim_time += dt

    def beak_point(self):
        x, y, w, h = self.draw_rect()
        k = DRAW_SIZE / BEAK_BASE
        ox, oy = BEAK[self.facing]
        return self.x + ox * k, y + h / 2 + oy * k

    def _fire(self, target):
        sh = self.shoot
        sx, sy = self.beak_point()
        (ux, uy), _ = direction((sx, sy), target)
        self._projectiles.append(Projectile(sx, sy, ux * sh["projectile_speed"], uy * sh["projectile_speed"],
                                            damage=sh.get("damage", 1), owner="enemy",
                                            lifetime=sh["range"] / sh["projectile_speed"] + 0.3))
        self.shot_flash = SHOT_FLASH_TIME

    def _shoot_action(self):
        """Кадры выстрела: shoot (клюв), а если их нет в manifest, запасные attack."""
        try:
            from src.systems.assets import _load_manifest
            if f"{self.sprite}_shoot_{self.facing}_1" in _load_manifest():
                return "shoot"
        except ImportError:
            pass
        return "attack"

    def frame_key(self):
        if self.sprite not in ANIMATED_SPRITES:
            return self.sprite
        if self.anim == "shoot":
            n = 2 if self.shot_flash > 0 else 1
            return f"{self.sprite}_{self._shoot_action()}_{self.facing}_{n}"
        if self.anim == "attack":
            n = 2 if self.state == "strike" else 1
        else:
            n = int(self.anim_time * FRAME_RATE[self.anim]) % FRAME_COUNT[self.anim] + 1
        return f"{self.sprite}_{self.anim}_{self.facing}_{n}"

    def draw_rect(self):
        """Где рисуется картинка: ноги стоят на нижнем крае хитбокса."""
        top = self.y + self.SIZE / 2 - DRAW_SIZE * FEET
        return (self.x - DRAW_SIZE / 2, top, DRAW_SIZE, DRAW_SIZE)

    def draw(self, surface):
        import pygame
        x, y, w, h = self.draw_rect()
        try:
            from src.systems.assets import get_image
            surface.blit(get_image(self.frame_key(), (w, h)), (x, y))
        except ImportError:
            pygame.draw.rect(surface, (200, 60, 60), self.rect)
        if self.hurt_timer > 0:
            pygame.draw.rect(surface, (255, 255, 255), (x + 8, y + 4, w - 16, h - 6), 2)
        if self.state == "windup" and self.attack is not None:
            pygame.draw.circle(surface, (255, 200, 0), (int(self.x), int(y)), 4)
