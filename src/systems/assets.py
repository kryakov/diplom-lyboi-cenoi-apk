import json
import pygame
from src import settings

_cache = {}
_manifest = None
_PLACEHOLDER_COLORS = {"bg": (40, 50, 60), "player": (60, 200, 90), "enemy": (200, 60, 60),
                       "boss": (160, 30, 120), "npc": (230, 200, 60)}


def _load_manifest():
    global _manifest
    if _manifest is None:
        try:
            with open(settings.ASSETS_DIR / "manifest.json", encoding="utf-8") as f:
                _manifest = json.load(f)
        except (OSError, ValueError):
            _manifest = {}
    return _manifest


def get_image(key, size=(settings.TILE, settings.TILE)):
    cache_key = (key, tuple(size))
    if cache_key in _cache:
        return _cache[cache_key]
    surf = None
    rel = _load_manifest().get(key)
    if rel:
        try:
            surf = pygame.image.load(str(settings.ASSETS_DIR / rel)).convert_alpha()
            surf = pygame.transform.scale(surf, size)
        except (OSError, pygame.error):
            surf = None
    if surf is None:
        surf = pygame.Surface(size)
        surf.fill(_PLACEHOLDER_COLORS.get(key.split("_")[0], (255, 0, 255)))
    _cache[cache_key] = surf
    return surf