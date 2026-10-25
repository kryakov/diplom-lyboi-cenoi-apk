# Роль 4. Игрок и бой

Лог художника для роли «Игрок и бой». Общий справочник: `docs/ART_LOG.md`, стиль: `docs/ART.md`, данные: `docs/art_info.json`. Все числа измерены по картинкам и коду `main`.

## Картинки героя

- Ключи: `player_<действие>_<dir>_<n>`: `idle` (2 кадра), `walk` (4), `shoot` (2), `walkshoot` (4); 8 направлений; запасной `player_idle`.
- Файл 32×32, в игре `Player.SIZE = 20`: `get_image(key, (20, 20))` в `(x - 10, y - 10)`. Хитбокс 20×20 подходит.
- Габарит видимой фигуры в игре (x1, y1, x2, y2), px от центра: idle/shoot [-8.8, -9.4, 8.8, 9.4], walk/walkshoot [-8.8, -10.0, 8.8, 10.0].

## Пули

Пули героя: `fx_bullet_l<уровень>_player_<угол>_<1|2>` (32×32, рисуются 1:1, центр = центр снаряда; угол 0/45/90/135/180/225/270/315 против часовой: 0 вправо, 90 вверх, 180 влево, 270 вниз): уровень 1 слово `shoot` (жёлтое), 2 нули и единицы (голубые, с помехами), 3 производная `f'(x)` (белая). Два кадра мерцают 8 раз в секунду. Хитбокс не менять (круг 4–5 px). Пули уже повёрнуты в файлах, в коде не вращать. Код в `projectile.py`:

```python
# в __init__: self.age = 0.0; в update: self.age += dt
def draw(self, surface, level):  # level = state.level_index + 1
    import math
    from src.systems.assets import get_image
    who = "player" if self.owner == "player" else "boss"
    ang = round(math.degrees(math.atan2(-self.vy, self.vx)) / 45) * 45 % 360  # 0 вправо, 90 вверх
    n = int(self.age * 8) % 2 + 1
    surface.blit(get_image(f"fx_bullet_l{level}_{who}_{ang}_{n}", (32, 32)), (self.x - 16, self.y - 16))
```

`CombatSystem.draw` передаёт `state.level_index + 1`. Подробности: `docs/ART_LOG.md`, раздел 2.5.

## Что сделать в `player.py`

```python
import math
DIRS = ["e", "se", "s", "sw", "w", "nw", "n", "ne"]  # y вниз, как в pygame
FPS = {"walk": 8, "walkshoot": 8, "idle": 2}
COUNT = {"idle": 2, "walk": 4, "shoot": 2, "walkshoot": 4}

def dir8(dx, dy):
    a = math.degrees(math.atan2(dy, dx)) % 360
    return DIRS[int((a + 22.5) // 45) % 8]

def frame_key(action, direction, t, shot_flash):
    n = (2 if shot_flash > 0 else 1) if action == "shoot" else int(t * FPS[action]) % COUNT[action] + 1
    return f"player_{action}_{direction}_{n}"
```

- В `update`: запомнить `self.moving = bool(mx or my)`, `self.shooting = shooting`, при выстреле `self.shot_flash = 0.1` (убывает с dt).
- Направление: при стрельбе `dir8(*self.aim)`, иначе при движении `dir8(mx, my)`, иначе прежнее.
- Действие: `walkshoot`, если стреляет и идёт; `shoot`, если стреляет стоя; `walk`, если идёт; иначе `idle`.
- Кадр: `walk`/`walkshoot` 8 к/с, `idle` 2 к/с, `shoot`: кадр 2 в течение 0,1 с после выстрела, потом кадр 1. При смене действия счётчик сбрасывать, при смене только направления не сбрасывать.
- **Убрать белый кружок руки** (`pygame.draw.circle(... HAND ...)`): рука нарисована в кадрах.
- Мигание неуязвимости (`visible`) оставить.

## Точка вылета снаряда (кончик пальца)

Смещение от центра героя, px игры; снаряд создавать в `(x + ox, y + oy)`, скорость вдоль прицела. С нынешним `HAND = 14` снаряд вылетает в стороне от пальца: до 14 px при стрельбе вверх.

| | s | se | e | ne | n | nw | w | sw |
|---|---|---|---|---|---|---|---|---|
| `player` | (-5, 8) | (3, 7) | (5, 5) | (7, 1) | (6, -1) | (-8, -7) | (-5, 5) | (-8, 7) |
