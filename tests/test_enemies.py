import json
import math
import tempfile
import unittest
from pathlib import Path

from src.entities.enemy import Enemy
from src.entities.projectile import Projectile
from src.systems.ai import alive_count, create_enemy, spawn_all

MELEE = {"id": "m", "name": "М", "kind": "melee", "sprite": "enemy_m", "hp": 2, "speed": 100,
         "contact_damage": 1, "attack": {"range": 36, "windup": 0.4, "cooldown": 1.0, "damage": 1}}
BOSS = {"id": "boss_t", "name": "Б", "kind": "boss", "sprite": "boss_t", "hp": 10, "speed": 80,
        "contact_damage": 1, "attacks": [
            {"type": "fan", "projectiles": 5, "spread_deg": 60, "speed": 260, "windup": 0.5, "damage": 1, "cooldown": 2.0},
            {"type": "dash", "speed": 500, "duration": 0.5, "windup": 0.6, "damage": 1, "cooldown": 2.0}]}


class OpenRoom:

    def __init__(self, walls=()):
        self.walls = list(walls)

    def blocked(self, rect):
        x, y, w, h = tuple(rect)
        if x < 0 or y < 0 or x + w > 960 or y + h > 540:
            return True
        return any(x < wx + ww and wx < x + w and y < wy + wh and wy < y + h for wx, wy, ww, wh in self.walls)

    def slide(self, rect, dx, dy):
        x, y, w, h = tuple(rect)
        if dx and not self.blocked((x + dx, y, w, h)):
            x += dx
        if dy and not self.blocked((x, y + dy, w, h)):
            y += dy
        return (x, y)


def run(enemy, room, target, seconds, dt=0.02):
    for _ in range(int(seconds / dt)):
        enemy.update(dt, room, target)


class TestMelee(unittest.TestCase):
    def test_chases_player(self):
        e = Enemy(MELEE, (100, 270))
        e.update(0.1, OpenRoom(), (500, 270))
        self.assertAlmostEqual(e.x, 110)

    def test_attack_cycle(self):
        e = Enemy(MELEE, (100, 270))
        target = (120, 270)
        e.update(0.02, OpenRoom(), target)
        self.assertEqual(e.state, "windup")
        self.assertIsNone(e.attack_hitbox())
        run(e, OpenRoom(), target, 0.42)
        self.assertEqual(e.state, "strike")
        box, dmg = e.attack_hitbox()
        self.assertEqual(dmg, 1)
        bx, by, bw, bh = box
        self.assertTrue(bx <= target[0] <= bx + bw and by <= target[1] <= by + bh)
        run(e, OpenRoom(), target, 0.2)
        self.assertEqual(e.state, "cooldown")
        self.assertIsNone(e.attack_hitbox())
        run(e, OpenRoom(), target, 1.05)
        self.assertEqual(e.state, "windup")

    def test_dodge_possible(self):
        e = Enemy(MELEE, (100, 270))
        e.update(0.02, OpenRoom(), (120, 270))
        run(e, OpenRoom(), (300, 270), 0.42)
        box, _ = e.attack_hitbox()
        bx, by, bw, bh = box
        self.assertFalse(bx <= 300 <= bx + bw)

    def test_wall_blocks(self):
        wall = (150, 0, 20, 540)
        e = Enemy(MELEE, (100, 270))
        run(e, OpenRoom([wall]), (500, 270), 3.0)
        self.assertLessEqual(e.x + Enemy.SIZE / 2, 150 + 1e-6)

    def test_damage_and_death(self):
        e = Enemy(MELEE, (100, 270))
        e.take_damage(1)
        self.assertTrue(e.alive)
        e.take_damage(5)
        self.assertFalse(e.alive)
        self.assertEqual(e.hp, 0)
        e.update(0.5, OpenRoom(), (101, 270))
        self.assertIsNone(e.attack_hitbox())
        self.assertEqual(e.take_projectiles(), [])

    def test_take_projectiles_clears(self):
        e = Enemy(MELEE, (0, 0))
        e._projectiles.append(Projectile(0, 0, 1, 0, owner="enemy"))
        self.assertEqual(len(e.take_projectiles()), 1)
        self.assertEqual(e.take_projectiles(), [])


class TestLoader(unittest.TestCase):
    def test_create_and_spawn(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp) / "enemies"
            d.mkdir()
            (d / "m.json").write_text(json.dumps(MELEE, ensure_ascii=False), encoding="utf-8")
            self.assertIsInstance(create_enemy("m", (1, 2), tmp), Enemy)

            class R:
                enemy_spawns = [("m", (10, 10)), ("m", (50, 50))]

            enemies = spawn_all(R, tmp)
            self.assertEqual(len(enemies), 2)
            self.assertEqual(alive_count(enemies), 2)
            enemies[0].take_damage(99)
            self.assertEqual(alive_count(enemies), 1)

    def test_unknown_enemy(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                create_enemy("ghost", (0, 0), tmp)


if __name__ == "__main__":
    unittest.main()
