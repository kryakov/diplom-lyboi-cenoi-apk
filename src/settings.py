from pathlib import Path

SCREEN_W = 960
SCREEN_H = 540
FPS = 60
TITLE = "Диплом любой ценой"
FULLSCREEN = True           # F11 в игре переключает окно и полный экран

TILE = 30
ROOM_W_TILES = SCREEN_W // TILE
ROOM_H_TILES = SCREEN_H // TILE

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

PLAYER_MAX_HEALTH = 5
PLAYER_SPEED = 220
INVULN_TIME = 1.0

RED_DIPLOMA_MAX_DEATHS = 0
DIFFICULTY_ORDER = ("easy", "normal", "hard")
DIFFICULTY = "normal"
DIFFICULTIES = {
      "easy":   {"name": "Лёгкая",  "hp": 0.6, "speed": 0.8, "cooldown": 1.4, "windup": 1.3,  "projectiles": 0.6},
      "normal": {"name": "Средняя", "hp": 0.8, "speed": 0.9, "cooldown": 1.2, "windup": 1.15, "projectiles": 0.8},
      "hard":   {"name": "Сложная", "hp": 1.0, "speed": 1.0, "cooldown": 1.0, "windup": 1.0,  "projectiles": 1.0},
  }