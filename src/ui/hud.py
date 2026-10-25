from src.systems.assets import get_image

BAR_SIZE = (320, 44)
BAR_POS = (16, 12)
MAX_HEALTH = 5
HIT_FRAMES = 6
FRAME_TIME = 0.05


class Hud:

    def __init__(self):
        self.health = None
        self.hit_health = None
        self.hit_time = None

    def update(self, dt, health):
        health = max(0, min(MAX_HEALTH, health))
        if self.health is not None:
            if health < self.health:
                self.hit_health = health
                self.hit_time = 0.0
            elif health > self.health:
                self.hit_time = None
        self.health = health
        if self.hit_time is not None:
            self.hit_time += dt

    def draw(self, surface):
        if self.health is None:
            return
        key = f"ui_health_{self.health}"
        if self.hit_time is not None:
            frame = int(self.hit_time / FRAME_TIME) + 1
            if frame <= HIT_FRAMES and self.hit_health < MAX_HEALTH:
                key = f"ui_health_hit_{self.hit_health}_{frame}"
            else:
                self.hit_time = None
        surface.blit(get_image(key, BAR_SIZE), BAR_POS)
