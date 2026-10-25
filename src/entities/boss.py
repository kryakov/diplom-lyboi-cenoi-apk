import math

from src.entities.enemy import direction
from src.entities.projectile import Projectile

# Спрайты боссов, для которых нарисованы анимации (ключи вида <sprite>_<действие>_<сторона>_<кадр>).
ANIMATED_SPRITES = ("boss_level1", "boss_level2", "boss_level3")
DIRS = ["e", "se", "s", "sw", "w", "nw", "n", "ne"]
FRAME_COUNT = {"idle": 2, "walk": 4, "shoot": 2}
FRAME_RATE = {"idle": 2, "walk": 8, "dash": 16}
SHOT_FLASH_TIME = 0.1
DRAW_SIZE = 64              # размер картинки босса на экране (хитбокс SIZE = 56 не меняется)
FEET = 60 / 64              # низ ног в кадре (доля высоты картинки)
MUZZLE_BASE = 56            # точки вылета в логе измерены для размера 56
# Откуда вылетают снаряды (смещение от центра, пиксели игры, по сторонам). Из docs/ART_LOG.md.
_RIGHT_HAND = {"s": (-13, 22), "se": (9, 20), "e": (13, 13), "ne": (19, 3),
               "n": (17, -3), "nw": (-21, -20), "w": (-13, 13), "sw": (-21, 20)}
MUZZLE = {
    "boss_level1": _RIGHT_HAND,
    "boss_level2": _RIGHT_HAND,
    "boss_level3": {"s": (13, 18), "se": (21, 17), "e": (13, 10), "ne": (21, -24),
                    "n": (-17, -6), "nw": (-19, -1), "w": (-13, 10), "sw": (-9, 17)},
}


def dir8(dx, dy):
    angle = math.degrees(math.atan2(dy, dx)) % 360
    return DIRS[int((angle + 22.5) // 45) % 8]


class Boss:
    SIZE = 56
    PROJECTILE_LIFETIME = 4.0
    PROJECTILE_RADIUS = 5
    DEFAULT_WINDUP = 0.5
    FIRST_ATTACK_DELAY = 1.5
    KEEP_DISTANCE = 150

    def __init__(self, data, pos):
        self.id = data["id"]
        self.name = data["name"]
        self.kind = data["kind"]
        self.sprite = data["sprite"]
        self.max_hp = data["hp"]
        self.hp = data["hp"]
        self.speed = data["speed"]
        self.contact_damage = data["contact_damage"]
        self.attacks = data["attacks"]
        self.x, self.y = float(pos[0]), float(pos[1])
        self.alive = True
        self.hurt_timer = 0.0
        self._projectiles = []
        self.state = "rest"
        self.timer = self.FIRST_ATTACK_DELAY
        self.attack_index = 0
        self.current = None
        self.dash_dir = (1.0, 0.0)
        self.facing = "s"
        self.moving = False
        self.anim = "idle"
        self.anim_time = 0.0
        self.shot_flash = 0.0

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
        if not self.alive or self.state != "dash":
            return None
        return (self.rect, self.current["damage"])

    def _move(self, room, dx, dy):
        h = self.SIZE / 2
        before = (self.x, self.y)
        nx, ny = room.slide((self.x - h, self.y - h, self.SIZE, self.SIZE), dx, dy)
        self.x, self.y = nx + h, ny + h
        return (self.x, self.y) != before

    def _fire_fan(self, target):
        atk = self.current
        (ux, uy), _ = direction(self.center, target)
        center_angle = math.degrees(math.atan2(uy, ux))
        count = max(1, int(atk["projectiles"]))
        spread = atk["spread_deg"]
        self.shot_flash = SHOT_FLASH_TIME
        k = DRAW_SIZE / MUZZLE_BASE
        ox, oy = MUZZLE.get(self.sprite, {}).get(self.facing, (0, 0))
        dx, dy, dw, dh = self.draw_rect()
        ox, oy = ox * k, dy + dh / 2 - self.y + oy * k
        for i in range(count):
            offset = 0.0 if count == 1 else spread * (i / (count - 1) - 0.5)
            self._projectiles.append(Projectile.aimed(
                self.x + ox, self.y + oy, center_angle + offset, atk["speed"],
                damage=atk["damage"], owner="enemy",
                radius=self.PROJECTILE_RADIUS, lifetime=self.PROJECTILE_LIFETIME))

    def update(self, dt, room, target):
        if not self.alive:
            return
        self.hurt_timer = max(0.0, self.hurt_timer - dt)
        self.shot_flash = max(0.0, self.shot_flash - dt)
        dir_, dist = direction(self.center, target)
        if self.state != "dash":
            self.facing = dir8(*dir_)
        self.moving = False

        if self.state == "rest":
            self.timer -= dt
            if dist > self.KEEP_DISTANCE:
                self.moving = self._move(room, dir_[0] * self.speed * dt, dir_[1] * self.speed * dt)
            if self.timer <= 0:
                self.current = self.attacks[self.attack_index % len(self.attacks)]
                self.attack_index += 1
                self.state = "windup"
                self.timer = self.current.get("windup", self.DEFAULT_WINDUP)
                self.dash_dir = dir_
                self.facing = dir8(*dir_)

        elif self.state == "windup":
            self.timer -= dt
            if self.timer <= 0:
                if self.current["type"] == "fan":
                    self._fire_fan(target)
                    self.state = "rest"
                    self.timer = self.current["cooldown"]
                else:
                    self.state = "dash"
                    self.timer = self.current["duration"]
                    self.facing = dir8(*self.dash_dir)

        elif self.state == "dash":
            self.timer -= dt
            speed = self.current["speed"]
            moved = self._move(room, self.dash_dir[0] * speed * dt, self.dash_dir[1] * speed * dt)
            if self.timer <= 0 or not moved:
                self.state = "rest"
                self.timer = self.current["cooldown"]

        if self.state == "dash":
            anim = "dash"
        elif self.state == "windup" or self.shot_flash > 0:
            anim = "shoot"
        elif self.moving:
            anim = "walk"
        else:
            anim = "idle"
        if anim != self.anim:
            self.anim = anim
            self.anim_time = 0.0
        else:
            self.anim_time += dt

    def frame_key(self):
        if self.sprite not in ANIMATED_SPRITES:
            return self.sprite
        if self.anim == "shoot":
            n = 2 if self.shot_flash > 0 else 1
            action = "shoot"
        elif self.anim == "dash":
            action = "walk"
            n = int(self.anim_time * FRAME_RATE["dash"]) % FRAME_COUNT["walk"] + 1
        else:
            action = self.anim
            n = int(self.anim_time * FRAME_RATE[action]) % FRAME_COUNT[action] + 1
        return f"{self.sprite}_{action}_{self.facing}_{n}"

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
            pygame.draw.rect(surface, (160, 30, 120), self.rect)
        frame = (x + 6, y + 2, w - 12, h - 4)
        if self.hurt_timer > 0:
            pygame.draw.rect(surface, (255, 255, 255), frame, 3)
        if self.state == "windup":
            pygame.draw.rect(surface, (255, 200, 0), frame, 3)
        elif self.state == "dash":
            pygame.draw.rect(surface, (255, 70, 70), frame, 3)
        bar_w = 120
        bx, by = self.x - bar_w / 2, y - 12
        pygame.draw.rect(surface, (40, 40, 40), (bx, by, bar_w, 7))
        pygame.draw.rect(surface, (210, 50, 50), (bx, by, bar_w * self.hp / self.max_hp, 7))
