from src.entities.projectile import rects_overlap


def read_controls():
    import pygame
    keys = pygame.key.get_pressed()
    right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
    left = keys[pygame.K_LEFT] or keys[pygame.K_a]
    down = keys[pygame.K_DOWN] or keys[pygame.K_s]
    up = keys[pygame.K_UP] or keys[pygame.K_w]
    mx = (1 if right else 0) - (1 if left else 0)
    my = (1 if down else 0) - (1 if up else 0)
    return (mx, my), pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]


class CombatSystem:
    def __init__(self):
        self.projectiles = []

    def add(self, projectiles):
        self.projectiles.extend(projectiles)

    def clear(self):
        self.projectiles = []

    def update(self, dt, room, player, enemies, state):
        events = []

        for e in enemies:
            if e.alive:
                self.projectiles.extend(e.take_projectiles())

        for p in self.projectiles:
            p.update(dt, room)

        for p in self.projectiles:
            if not p.alive:
                continue
            if p.owner == "player":
                for e in enemies:
                    if e.alive and rects_overlap(p.rect, e.rect):
                        e.take_damage(p.damage)
                        p.alive = False
                        events.append("enemy_killed" if not e.alive else "enemy_hit")
                        break
            else:
                if rects_overlap(p.rect, player.rect):
                    p.alive = False
                    self._hit_player(player, p.damage, state, events)

        for e in enemies:
            if not e.alive:
                continue
            if e.contact_damage and rects_overlap(e.rect, player.rect):
                self._hit_player(player, e.contact_damage, state, events)
            box = e.attack_hitbox()
            if box is not None:
                rect, damage = box
                if rects_overlap(rect, player.rect):
                    self._hit_player(player, damage, state, events)

        self.projectiles = [p for p in self.projectiles if p.alive]
        return events

    @staticmethod
    def _hit_player(player, damage, state, events):
        result = player.take_hit(damage, state)
        if result == "hit":
            events.append("player_hit")
        elif result == "dead":
            events.append("player_dead")

    def draw(self, surface, level=None):
        for p in self.projectiles:
            p.draw(surface, level)
