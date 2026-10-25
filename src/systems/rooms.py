"""Комната: стены, дверь, спавны, столкновения. Владелец: роль 3 «Уровни и комнаты».
Не зависит от pygame (прямоугольники — кортежи (x, y, w, h) в пикселях), поэтому тестируется без окна.
Игрок, враги и снаряды спрашивают у комнаты, можно ли им туда двигаться.
"""
import math

from src import settings


def _px(rect_tiles, tile):
    return tuple(v * tile for v in rect_tiles)


def intersects(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


class Room:
    def __init__(self, data, tile=settings.TILE):
        self.tile = tile
        self.id = data["id"]
        self.name = data["name"]
        self.type = data["type"]
        self.background = data["background"]
        self.size_px = (data["size"][0] * tile, data["size"][1] * tile)
        self.walls = [_px(w, tile) for w in data["walls"]]
        # стены выложены по клеткам: проверка «есть ли стена в этих клетках» вместо перебора всех стен
        self._wall_cells = {(cx, cy) for wx, wy, ww, wh in data["walls"]
                            for cx in range(wx, wx + ww) for cy in range(wy, wy + wh)}
        d = data.get("door")
        self.door = _px(d["pos"], tile) if d else None
        self.door_locked_until_clear = bool(d and d.get("locked_until_clear"))
        sx, sy = data["player_spawn"]
        self.player_spawn = (sx * tile + tile // 2, sy * tile + tile // 2)   # центр клетки
        self.enemy_spawns = [(e["type"], (e["pos"][0] * tile + tile // 2, e["pos"][1] * tile + tile // 2))
                             for e in data["enemies"]]
        self.npcs = [(n["id"], (n["pos"][0] * tile + tile // 2, n["pos"][1] * tile + tile // 2), n["dialogue"])
                     for n in data["npcs"]]
        self.pickups = [(p["kind"], (p["pos"][0] * tile + tile // 2, p["pos"][1] * tile + tile // 2), p.get("amount", 1))
                        for p in data["pickups"]]
        self.cleared = not self.enemy_spawns       # в мирной комнате дверь свободна сразу

    # ---------- дверь ----------
    def set_enemies_alive(self, count):
        """Вызывает game_scene каждый кадр (или при смерти врага)."""
        self.cleared = count <= 0

    @property
    def door_open(self):
        if self.door is None:
            return False
        return (not self.door_locked_until_clear) or self.cleared

    def exit_reached(self, rect):
        """True, если прямоугольник игрока вошёл в открытую дверь."""
        return self.door_open and intersects(tuple(rect), self.door)

    # ---------- столкновения ----------
    def blocked(self, rect):
        r = tuple(rect)
        x, y, w, h = r
        t = self.tile
        cells = self._wall_cells
        for cx in range(math.floor(x / t), math.ceil((x + w) / t)):
            for cy in range(math.floor(y / t), math.ceil((y + h) / t)):
                if (cx, cy) in cells:
                    return True
        if self.door is not None and not self.door_open and intersects(r, self.door):
            return True
        return False

    def slide(self, rect, dx, dy):
        """Сдвинуть прямоугольник на (dx, dy) с «скольжением» вдоль стен.
        Возвращает новые (x, y). Оси проверяются раздельно."""
        x, y, w, h = tuple(rect)
        if dx and not self.blocked((x + dx, y, w, h)):
            x += dx
        if dy and not self.blocked((x, y + dy, w, h)):
            y += dy
        return (x, y)

    # ---------- предметы ----------
    def collect_pickups(self, rect, size=settings.TILE):
        """Подобрать предметы, которых касается rect. Возвращает список (kind, amount) и убирает их из комнаты.
        game_scene применяет результат: for kind, amount in ...: if kind == 'heal': state.heal(amount)."""
        got, left = [], []
        for kind, (cx, cy), amount in self.pickups:
            item = (cx - size // 2, cy - size // 2, size, size)
            if intersects(tuple(rect), item):
                got.append((kind, amount))
            else:
                left.append((kind, (cx, cy), amount))
        self.pickups = left
        return got