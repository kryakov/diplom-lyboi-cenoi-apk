import math

from src import settings
from src.entities.projectile import Projectile

DIRS = ["e", "se", "s", "sw", "w", "nw", "n", "ne"]
FRAME_COUNT = {"idle": 2, "walk": 4, "shoot": 2, "walkshoot": 4}
FRAME_RATE = {"idle": 2, "walk": 8, "walkshoot": 8}
SHOT_FLASH_TIME = 0.1
HEAL_FLASH_TIME = 0.36       # после кофе герой мигает коричневым
HEAL_BLINK = 0.08
DRAW_SIZE = 48              # размер картинки героя на экране (как у врагов)
FEET = 31 / 32              # низ ног в кадре (доля высоты картинки)
# Кончик пальца относительно центра картинки при размере 20 px (docs/ART_LOG.md, раздел 3.3); масштабируется под DRAW_SIZE.
MUZZLE_BASE = 20
MUZZLE = {"s": (-5, 8), "se": (3, 7), "e": (5, 5), "ne": (7, 1),
          "n": (6, -1), "nw": (-8, -7), "w": (-5, 5), "sw": (-8, 7)}


def dir8(dx, dy):
    angle = math.degrees(math.atan2(dy, dx)) % 360
    return DIRS[int((angle + 22.5) // 45) % 8]


class Player:
    SIZE = 24
    SHOT_COOLDOWN = 0.40
    SHOT_SPEED = 520
    SHOT_DAMAGE = 1
    SHOT_LIFETIME = 0.8

    def __init__(self, pos):
        self.x, self.y = float(pos[0]), float(pos[1])
        self.aim = (1.0, 0.0)
        self.cooldown = 0.0
        self.invuln = 0.0
        self.facing = "s"
        self.action = "idle"
        self.anim_time = 0.0
        self.shot_flash = 0.0
        self.heal_flash = 0.0

    @property
    def rect(self):
        h = self.SIZE / 2
        return (self.x - h, self.y - h, self.SIZE, self.SIZE)

    @property
    def center(self):
        return (self.x, self.y)

    @property
    def visible(self):
        return not (self.invuln > 0 and int(self.invuln * 10) % 2 == 0)

    def teleport(self, pos):
        self.x, self.y = float(pos[0]), float(pos[1])
        self.cooldown = 0.0
        self.invuln = 0.0
        self.shot_flash = 0.0
        self.heal_flash = 0.0

    def on_heal(self):
        self.heal_flash = HEAL_FLASH_TIME

    def update(self, dt, room, move, aim_point, shooting):
        self.cooldown = max(0.0, self.cooldown - dt)
        self.heal_flash = max(0.0, self.heal_flash - dt)
        self.invuln = max(0.0, self.invuln - dt)
        self.shot_flash = max(0.0, self.shot_flash - dt)

        mx, my = move
        moving = bool(mx or my)
        length = math.hypot(mx, my)
        if length > 1:
            mx, my = mx / length, my / length
        if moving:
            h = self.SIZE / 2
            nx, ny = room.slide((self.x - h, self.y - h, self.SIZE, self.SIZE),
                                mx * settings.PLAYER_SPEED * dt, my * settings.PLAYER_SPEED * dt)
            self.x, self.y = nx + h, ny + h

        ax, ay = aim_point[0] - self.x, aim_point[1] - self.y
        d = math.hypot(ax, ay)
        if d > 1e-6:
            self.aim = (ax / d, ay / d)

        if shooting:
            self.facing = dir8(*self.aim)
        elif moving:
            self.facing = dir8(mx, my)
        if shooting and moving:
            action = "walkshoot"
        elif shooting:
            action = "shoot"
        elif moving:
            action = "walk"
        else:
            action = "idle"
        if action != self.action:
            self.action = action
            self.anim_time = 0.0
        else:
            self.anim_time += dt

        shots = []
        if shooting and self.cooldown == 0.0:
            self.cooldown = self.SHOT_COOLDOWN
            self.shot_flash = SHOT_FLASH_TIME
            sx, sy = self.muzzle_point()
            # летим из кончика пальца ровно в точку прицела, иначе пуля идёт параллельно и мажет
            dx, dy = aim_point[0] - sx, aim_point[1] - sy
            dist = math.hypot(dx, dy)
            ux, uy = (dx / dist, dy / dist) if dist > 1 else self.aim
            shots.append(Projectile(sx, sy,
                                    ux * self.SHOT_SPEED, uy * self.SHOT_SPEED,
                                    damage=self.SHOT_DAMAGE, owner="player",
                                    lifetime=self.SHOT_LIFETIME))
        return shots

    def draw_top(self):
        """Верх картинки: ноги стоят на нижнем крае хитбокса."""
        return self.y + self.SIZE / 2 - DRAW_SIZE * FEET

    def muzzle_point(self):
        k = DRAW_SIZE / MUZZLE_BASE
        ox, oy = MUZZLE[self.facing]
        return self.x + ox * k, self.draw_top() + DRAW_SIZE / 2 + oy * k

    def take_hit(self, amount, state):
        if self.invuln > 0 or not state.is_alive:
            return "ignored"
        died = state.damage(amount)
        self.invuln = settings.INVULN_TIME
        return "dead" if died else "hit"

    def frame_key(self):
        if self.action == "shoot":
            n = 2 if self.shot_flash > 0 else 1
        else:
            n = int(self.anim_time * FRAME_RATE[self.action]) % FRAME_COUNT[self.action] + 1
        # кадр идёт как обычно, через каждые 0.08 с подменяется коричневой копией player_brown_*
        brown = self.heal_flash > 0 and int(self.heal_flash / HEAL_BLINK) % 2 == 0
        return f"player_{'brown_' if brown else ''}{self.action}_{self.facing}_{n}"

    def draw(self, surface):
        if not self.visible:
            return
        from src.systems.assets import get_image
        surface.blit(get_image(self.frame_key(), (DRAW_SIZE, DRAW_SIZE)),
                     (self.x - DRAW_SIZE / 2, self.draw_top()))
