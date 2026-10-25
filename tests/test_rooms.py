import json
import tempfile
import unittest
from pathlib import Path

from src.systems.level_loader import load_levels, load_room
from src.systems.rooms import Room, intersects

T = 30
DATA = {
    "id": "t_room", "name": "Тест", "type": "battle", "background": "bg_test", "size": [32, 18],
    "player_spawn": [4, 9],
    "walls": [[0, 0, 32, 1], [0, 17, 32, 1], [0, 0, 1, 18], [31, 0, 1, 8], [31, 10, 1, 8], [14, 5, 2, 8]],
    "door": {"pos": [31, 8, 1, 2], "locked_until_clear": True},
    "enemies": [{"type": "english_melee", "pos": [20, 4]}],
    "npcs": [], "pickups": [{"kind": "heal", "pos": [8, 3], "amount": 1}],
}


class TestRoom(unittest.TestCase):
    def setUp(self):
        self.room = Room(DATA, T)

    def test_units_and_spawn(self):
        self.assertEqual(self.room.size_px, (960, 540))
        self.assertEqual(self.room.player_spawn, (4 * T + 15, 9 * T + 15))
        self.assertEqual(self.room.enemy_spawns[0][1], (20 * T + 15, 4 * T + 15))

    def test_intersects(self):
        self.assertTrue(intersects((0, 0, 10, 10), (5, 5, 10, 10)))
        self.assertFalse(intersects((0, 0, 10, 10), (10, 0, 10, 10)))   # касание — не пересечение

    def test_wall_blocks_and_slide(self):
        self.assertTrue(self.room.blocked((10, 100, 20, 20)))            # левая рамка
        self.assertFalse(self.room.blocked((100, 100, 20, 20)))
        # идём вправо в стену (x=14*30=420): упрёмся, но по y скользим
        x, y = self.room.slide((395, 200, 20, 20), 10, 5)
        self.assertEqual((x, y), (395, 205))

    def test_door_locked_then_open(self):
        door_rect = (31 * T, 8 * T, 20, 20)
        self.assertFalse(self.room.door_open)
        self.assertTrue(self.room.blocked(door_rect))
        self.assertFalse(self.room.exit_reached(door_rect))
        self.room.set_enemies_alive(0)
        self.assertTrue(self.room.door_open)
        self.assertFalse(self.room.blocked(door_rect))
        self.assertTrue(self.room.exit_reached(door_rect))

    def test_peaceful_room_door_free(self):
        d = dict(DATA, enemies=[], door={"pos": [31, 8, 1, 2], "locked_until_clear": False})
        r = Room(d, T)
        self.assertTrue(r.door_open)

    def test_pickups(self):
        far = self.room.collect_pickups((300, 300, 20, 20))
        self.assertEqual(far, [])
        self.assertEqual(len(self.room.pickups), 1)
        near = self.room.collect_pickups((8 * T, 3 * T, 20, 20))
        self.assertEqual(near, [("heal", 1)])
        self.assertEqual(self.room.pickups, [])
        self.assertEqual(self.room.collect_pickups((8 * T, 3 * T, 20, 20)), [])

    def test_no_door(self):
        d = {k: v for k, v in DATA.items() if k != "door"}
        r = Room(d, T)
        self.assertFalse(r.door_open)
        self.assertFalse(r.exit_reached((0, 0, 5, 5)))


class TestLoader(unittest.TestCase):
    def test_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "rooms").mkdir()
            (base / "rooms" / "t_room.json").write_text(json.dumps(DATA, ensure_ascii=False), encoding="utf-8")
            (base / "levels.json").write_text(json.dumps(
                {"levels": [{"id": "level1", "name": "Печерка", "rooms": ["t_room"]}]}, ensure_ascii=False), encoding="utf-8")
            self.assertEqual(load_room("t_room", base).name, "Тест")
            self.assertEqual(load_levels(base), ([["t_room"]], ["Печерка"]))


if __name__ == "__main__":
    unittest.main()