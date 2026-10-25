from collections import deque
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.systems.level_loader import load_levels, load_room  # noqa: E402
from src.systems.rooms import intersects  # noqa: E402

PLAYER, ENEMY, BOSS = 24, 24, 56


def tile_of(room, point):
    return int(point[0] // room.tile), int(point[1] // room.tile)


def reachable(room):
    t = room.tile
    w, h = room.size_px[0] // t, room.size_px[1] // t

    def free(tx, ty):
        cx, cy = tx * t + t / 2, ty * t + t / 2
        rect = (cx - PLAYER / 2, cy - PLAYER / 2, PLAYER, PLAYER)
        return not any(intersects(rect, wall) for wall in room.walls)

    start = tile_of(room, room.player_spawn)
    seen, queue = {start}, deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if 0 <= n[0] < w and 0 <= n[1] < h and n not in seen and free(*n):
                seen.add(n)
                queue.append(n)
    return seen


def check(room):
    errors = []

    def stands_free(size, center):
        half = size / 2
        return not any(intersects((center[0] - half, center[1] - half, size, size), wall) for wall in room.walls)

    if not stands_free(PLAYER, room.player_spawn):
        errors.append("старт героя в стене")
    for kind, pos in room.enemy_spawns:
        if not stands_free(BOSS if kind.startswith("boss") else ENEMY, pos):
            errors.append(f"{kind} в клетке {tile_of(room, pos)} не помещается (стена рядом)")

    seen = reachable(room)
    if room.door is None:
        errors.append("нет двери")
    else:
        t = room.tile
        dx, dy, dw, dh = room.door
        cells = {(tx, ty) for tx in range(dx // t, (dx + dw - 1) // t + 1) for ty in range(dy // t, (dy + dh - 1) // t + 1)}
        if not cells & seen:
            errors.append("до двери не дойти")
    targets = [("враг " + k, p) for k, p in room.enemy_spawns]
    targets += [("предмет " + k, p) for k, p, _ in room.pickups]
    targets += [("NPC " + i, p) for i, p, _ in room.npcs]
    for label, pos in targets:
        if tile_of(room, pos) not in seen:
            errors.append(f"{label} в клетке {tile_of(room, pos)} недостижим")
    return errors


def main():
    levels, _ = load_levels()
    total = 0
    for rooms in levels:
        for room_id in rooms:
            try:
                room = load_room(room_id)
            except (OSError, ValueError, KeyError) as e:
                print(f"{room_id}: не загрузилась ({e})")
                total += 1
                continue
            errors = check(room)
            print(f"{room_id}: {'OK' if not errors else '; '.join(errors)}")
            total += len(errors)
    print(f"Проблем: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())