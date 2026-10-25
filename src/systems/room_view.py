import pygame
from src import settings
from src.systems.assets import get_image

WALL_COLOR = (90, 90, 100)
DOOR_OPEN = (60, 170, 90)
DOOR_CLOSED = (170, 60, 60)
CLOSED_DOOR_ALPHA = 150
NPC_SIZE = 48
NPC_FEET = 31 / 32          # низ ног в кадре NPC (доля высоты картинки)
HEAL_SIZE = 32
HEAL_KEY = "fx_heal"
HEAL_FLOAT = "fx_heal_float_{}"   # стакан кофе покачивается и вращается: 8 кадров по 0.1 с
HEAL_FRAMES = 8
HEAL_FRAME_TIME = 0.1


def _has_image(key):
    try:
        from src.systems.assets import _load_manifest
        return key in _load_manifest()
    except ImportError:
        return False


def _draw_heal(surface, cx, cy):
    frame = int(pygame.time.get_ticks() / 1000 / HEAL_FRAME_TIME) % HEAL_FRAMES + 1
    for key in (HEAL_FLOAT.format(frame), HEAL_KEY):
        if _has_image(key):
            surface.blit(get_image(key, (HEAL_SIZE, HEAL_SIZE)), (cx - HEAL_SIZE // 2, cy - HEAL_SIZE // 2))
            return
    # пока нет картинки: белый кружок с красным крестом, чтобы было понятно, что это лечение
    pygame.draw.circle(surface, (28, 28, 46), (cx, cy), 11)
    pygame.draw.circle(surface, (244, 244, 240), (cx, cy), 10)
    pygame.draw.rect(surface, (214, 52, 52), (cx - 2, cy - 7, 5, 15))
    pygame.draw.rect(surface, (214, 52, 52), (cx - 7, cy - 2, 15, 5))


def npc_top_left(cx, cy):
    """NPC стоит ногами на нижнем крае своей клетки."""
    return cx - NPC_SIZE // 2, int(cy + settings.TILE / 2 - NPC_SIZE * NPC_FEET)


def draw_room(surface, room, debug=False):
    """Фон, закрытая дверь, лечилки и NPC. Стены нарисованы на фоне; серые прямоугольники только в режиме отладки."""
    surface.blit(get_image(room.background, room.size_px), (0, 0))
    if debug:
        for w in room.walls:
            pygame.draw.rect(surface, WALL_COLOR, w, 1)
        if room.door is not None:
            pygame.draw.rect(surface, DOOR_OPEN if room.door_open else DOOR_CLOSED, room.door, 2)
    elif room.door is not None and not room.door_open:
        x, y, w, h = room.door
        cover = pygame.Surface((w, h), pygame.SRCALPHA)
        cover.fill((*DOOR_CLOSED, CLOSED_DOOR_ALPHA))
        surface.blit(cover, (x, y))
    for kind, (cx, cy), _ in room.pickups:
        _draw_heal(surface, cx, cy)
    for npc_id, (cx, cy), _ in room.npcs:
        surface.blit(get_image(f"npc_{npc_id}", (NPC_SIZE, NPC_SIZE)), npc_top_left(cx, cy))
