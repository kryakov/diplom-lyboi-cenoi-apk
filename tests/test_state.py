import unittest

from src.core.state import GameState

LEVELS = [["a1", "a2"], ["b1"]]


class TestGameState(unittest.TestCase):
    def test_health_and_death(self):
        s = GameState(LEVELS)
        self.assertEqual(s.health, 5)
        self.assertFalse(s.damage(2))
        self.assertEqual(s.health, 3)
        self.assertTrue(s.damage(10))
        self.assertEqual(s.health, 0)
        self.assertFalse(s.damage(1))
        s.register_death()
        self.assertEqual((s.deaths, s.health), (1, 5))
        self.assertFalse(s.red_diploma)

    def test_heal_cap(self):
        s = GameState(LEVELS)
        s.damage(2)
        s.heal(10)
        self.assertEqual(s.health, s.max_health)

    def test_progress(self):
        s = GameState(LEVELS)
        self.assertEqual(s.current_room_id, "a1")
        self.assertEqual(s.advance_room(), "room")
        self.assertEqual(s.current_room_id, "a2")
        self.assertEqual(s.advance_room(), "level")
        self.assertEqual(s.current_room_id, "b1")
        self.assertEqual(s.advance_room(), "game_end")

    def test_red_diploma(self):
        s = GameState(LEVELS)
        self.assertTrue(s.red_diploma)
        s.register_death()
        self.assertFalse(s.red_diploma)

    def test_bad_levels(self):
        with self.assertRaises(ValueError):
            GameState([])
        with self.assertRaises(ValueError):
            GameState([["a"], []])


if __name__ == "__main__":
    unittest.main()
