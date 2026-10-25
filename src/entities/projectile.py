import math


def rects_overlap(a, b):
    ax, ay, aw, ah = tuple(a)
    bx, by, bw, bh = tuple(b)
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


class Projectile:
    def __init__(self, x, y, vx, vy, damage=1, owner="player", radius=4, lifetime=2.0):
        if owner not in ("player", "enemy"):
            raise ValueError("owner должен быть 'player' или 'enemy'")
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = float(vx), float(vy)
        self.damage = damage
        self.owner = owner
        self.radius = radius
        self.lifetime = lifetime
        self.alive = True
        self.age = 0.0

    @classmethod
    def aimed(cls, x, y, angle_deg, speed, **kw):
        a = math.radians(angle_deg)
        return cls(x, y, math.cos(a) * speed, math.sin(a) * speed, **kw)

    @property
    def rect(self):
        r = self.radius
        return (self.x - r, self.y - r, 2 * r, 2 * r)

    def update(self, dt, room=None):
        if not self.alive:
            return
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.age += dt
        self.lifetime -= dt
        if self.lifetime <= 0 or (room is not None and room.blocked(self.rect)):
            self.alive = False

    def angle(self):
        """Направление полёта, округлённое до 45 градусов: 0 вправо, 90 вверх, 180 влево, 270 вниз."""
        return round(math.degrees(math.atan2(-self.vy, self.vx)) / 45) * 45 % 360

    def draw(self, surface, level=None):
        """level = номер уровня 1..3: пуля-картинка fx_bullet_l<уровень>_<player|boss>_<угол>_<кадр>, иначе кружок.
        Картинка 32x32 уже повёрнута в файле, центр картинки = центр снаряда."""
        import pygame
        if level is not None:
            from src.systems import assets
            who = "player" if self.owner == "player" else "boss"
            key = f"fx_bullet_l{level}_{who}_{self.angle()}_{int(self.age * 8) % 2 + 1}"
            if key in assets._load_manifest():
                surface.blit(assets.get_image(key, (32, 32)), (self.x - 16, self.y - 16))
                return
        color = (255, 230, 90) if self.owner == "player" else (255, 90, 90)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)
