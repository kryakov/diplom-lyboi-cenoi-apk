"""Рисует картинки проекта (Pillow). Запуск: python tools/make_art.py; только проверка: python tools/make_art.py --check"""
import json
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "images")
MANIFEST = os.path.join(ROOT, "assets", "manifest.json")

PALETTE = {
    "outline": (28, 28, 46),
    # стены и пол
    "wall": (92, 92, 108),
    "wall_dark": (62, 62, 76),
    "wall_light": (116, 116, 132),
    "floor_a": (196, 176, 144),
    "floor_b": (186, 166, 135),
    "rug": (126, 70, 78),
    "rug_edge": (160, 96, 90),
    # дерево
    "wood": (164, 118, 72),
    "wood_light": (190, 146, 94),
    "wood_dark": (112, 72, 42),
    "shadow": (150, 132, 104),
    # доска, экраны, бумага
    "board": (30, 96, 56),
    "board_frame": (120, 82, 48),
    "chalk": (226, 236, 226),
    "screen": (150, 200, 220),
    "monitor": (52, 56, 70),
    "paper": (244, 244, 240),
    # герой: холодные цвета и жёлтый
    "teal": (38, 204, 182),
    "teal_dark": (22, 140, 138),
    "hair": (122, 74, 42),
    "hair_light": (164, 108, 62),
    "hair_dark": (88, 52, 30),
    "skin": (252, 208, 172),
    "skin_dark": (226, 172, 136),
    "pack": (248, 200, 56),
    "pack_dark": (204, 150, 36),
    "pants": (52, 72, 132),
    "book": (216, 62, 62),
    # прочее
    "leaf": (74, 156, 62),
    "leaf_dark": (46, 112, 50),
    "pot": (150, 84, 48),
    "box": (150, 104, 58),
    "door_in": (214, 244, 214),
    "door_out": (244, 224, 200),
    # препод, двор, интерфейс
    "hair_grey": (190, 190, 204),
    "hair_grey_dark": (130, 130, 146),
    "jacket": (122, 82, 52),
    "jacket_dark": (88, 56, 36),
    "path": (176, 176, 184),
    "shadow_ground": (110, 110, 120),
    "roof": (22, 50, 140),
    "roof_dark": (14, 34, 100),
    "base_dark": (96, 96, 108),
    "door_glass": (24, 26, 40),
    "step_a": (196, 196, 204),
    "step_b": (176, 176, 186),
    "bar_back": (230, 236, 232),
    "bar_green": (76, 184, 84),
    "bar_green_light": (120, 214, 120),
    "bar_yellow": (214, 200, 60),
    "bar_orange": (238, 140, 46),
    "bar_red": (226, 60, 56),
    "bar_green_dark": (54, 132, 60),
    "bar_yellow_light": (254, 240, 100),
    "bar_yellow_dark": (154, 144, 43),
    "bar_orange_light": (255, 180, 86),
    "bar_orange_dark": (171, 100, 33),
    "bar_red_light": (255, 100, 96),
    "bar_red_dark": (162, 43, 40),
    "hit_red_dark": (172, 28, 28),
    "face_dead": (170, 160, 130),
    "hit_face": (255, 150, 140),
    "hit_back": (255, 200, 196),
    "hit_red": (240, 40, 40),
    "hit_red_light": (255, 110, 100),
    "mouth": (150, 56, 60),
    "lens": (200, 226, 240),
    "pants_dark": (38, 52, 100),
    "shoe": (62, 62, 76),
    "boss_pants": (62, 62, 76),
    "boss_pants_dark": (52, 56, 70),
    "boss_shoe": (88, 56, 36),
    # корпус Львовки (по фото) и площадь перед ним
    "hse_blue": (76, 104, 178),
    "hse_blue_dark": (46, 66, 132),
    "hse_band": (200, 196, 186),
    "hse_light": (226, 228, 234),
    "glass": (118, 150, 196),
    "rail": (40, 72, 168),
    "brick": (84, 84, 92),
    "brick_dark": (62, 62, 70),
    "asphalt": (142, 142, 148),
    "asphalt_light": (154, 154, 160),
    "birch": (132, 192, 84),
    "birch_dark": (86, 146, 62),
    "birch_light": (176, 222, 120),
    # враги: тёплые цвета
    "enemy_red": (214, 68, 52),
    "enemy_red_dark": (150, 40, 40),
    "enemy_orange": (240, 150, 50),
    "enemy_orange_dark": (190, 100, 36),
}
P = PALETTE
TILE = 30


def save(img, key):
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, key + ".png"))
    data = {}
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            data = json.load(f)
    data[key] = "images/%s.png" % key
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def outline(img, color):
    """Тёмный контур 1 пиксель вокруг непрозрачных пикселей."""
    src = img.copy().load()
    dst = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if src[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3]:
                    dst[x, y] = color + (255,)
                    break


# ---------------------------------------------------------------- фоны
# Фон рисуется в половинном разрешении 480x270 (клетка 15 px) и увеличивается в 2 раза,
# чтобы пиксель был крупный, как у спрайтов. Предметы рисуются на отдельном слое и
# получают тёмный контур 1 px, как персонажи.
HW, HH, HT = 480, 270, TILE // 2
ARROW = ["...K...", "..KWK..", ".KWWWK.", "KWWWWWK", "..KWK..", "..KWK..", "..KKK.."]


def rect(d, x0, y0, x1, y1, col):
    """Прямоугольник по пикселям включительно."""
    d.rectangle([x0, y0, x1, y1], fill=P[col])


def disc(d, cx, cy, r, col):
    """Пиксельный круг без сглаживания."""
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r:
                d.point((x, y), fill=P[col])


def new_layer():
    return Image.new("RGBA", (HW, HH), (0, 0, 0, 0))


def lay_on(base, lay):
    """Слой с предметами: обвести контуром и положить на фон."""
    outline(lay, P["outline"])
    base.alpha_composite(lay)


def arrow(img, cx, cy):
    stamp(img, ARROW, cx - 3, cy - 3, {}, line=False)


def doorway(d, img, cx_cell, y0, col, frame):
    """Проём шириной 2 клетки: светлый порог, косяки, стрелка. Не затемнён."""
    x0 = cx_cell * HT
    rect(d, x0, y0, x0 + 2 * HT - 1, y0 + HT - 1, col)
    rect(d, x0, y0, x0 + 1, y0 + HT - 1, frame)
    rect(d, x0 + 2 * HT - 2, y0, x0 + 2 * HT - 1, y0 + HT - 1, frame)
    arrow(img, x0 + HT, y0 + HT // 2)


def finish(img):
    return img.resize((HW * 2, HH * 2), Image.NEAREST)


def floor_boards(d, x0, y0, x1, y1, ca="floor_a", cb="floor_b"):
    """Дощатый пол: доски по 5 px поперёк комнаты, стыки вразбежку, мало контраста."""
    rect(d, x0, y0, x1 - 1, y1 - 1, ca)
    for i, y in enumerate(range(y0, y1, 5)):
        rect(d, x0, y + 4, x1 - 1, y + 4, cb)
        for x in range(x0 + (i * 17) % 45, x1, 45):
            rect(d, x, y, x, y + 3, cb)


def wall_bricks(d, x0, y0, x1, y1):
    rect(d, x0, y0, x1, y1, "wall")
    for y in range(y0 + 4, y1, 5):
        rect(d, x0, y, x1, y, "wall_dark")
        off = 0 if (y // 5) % 2 else 5
        for x in range(x0 + off, x1, 10):
            rect(d, x, y - 4, x, y - 1, "wall_dark")


def cell(cx, cy, cw=1, ch=1):
    """Прямоугольник в клетках -> пиксели половинного холста (x0, y0, x1, y1) включительно."""
    return cx * HT, cy * HT, (cx + cw) * HT - 1, (cy + ch) * HT - 1


# Препятствия в фоне выровнены по клеткам: эти прямоугольники [x, y, ширина, высота]
# (клетки 30x30) роль 3 переносит в "walls" комнаты как есть. Внешняя рамка не указана.
HALL_DESKS = [(4, 4), (24, 4), (4, 13), (24, 13)]  # парта 4x1, под ней стул в двух средних клетках
HALL_WALLS = ([w for x, y in HALL_DESKS for w in ([x, y, 4, 1], [x + 1, y + 1, 2, 1])]
              + [[16, 1, 4, 1], [1, 1, 2, 1], [30, 1, 1, 1]])


def desk(d, cx, cy):
    """Парта сверху (клетки cx..cx+3, строка cy) и стул под ней (строка cy+1)."""
    x0, y0, x1, y1 = cell(cx, cy, 4, 1)
    rect(d, x0 + 20, y1 + 2, x1 - 20, y1 + 10, "wall")  # стул
    rect(d, x0 + 20, y1 + 9, x1 - 20, y1 + 10, "wall_dark")
    rect(d, x0 + 1, y0 + 2, x1 - 1, y1 - 1, "wood")
    rect(d, x0 + 1, y0 + 2, x1 - 1, y0 + 3, "wood_light")
    rect(d, x0 + 1, y1 - 2, x1 - 1, y1 - 1, "wood_dark")
    rect(d, x0 + 7, y0 + 5, x0 + 18, y0 + 10, "paper")
    rect(d, x0 + 7, y0 + 5, x0 + 8, y0 + 10, "book")
    rect(d, x0 + 34, y0 + 4, x0 + 46, y0 + 10, "monitor")
    rect(d, x0 + 35, y0 + 5, x0 + 45, y0 + 8, "screen")


def bg_level3_hall():
    """Львовка: аудитория. Вход снизу (клетки 15-16), выход сверху (клетки 26-27).
    Мебель стоит ровно по клеткам HALL_WALLS."""
    img = Image.new("RGBA", (HW, HH), P["wall"])
    d = ImageDraw.Draw(img)
    floor_boards(d, HT, HT, HW - HT, HH - HT)
    # стены по периметру: кирпичная кладка, светлая кромка, тень на полу у верхней стены
    wall_bricks(d, 0, 0, HW - 1, HT - 1)
    wall_bricks(d, 0, HH - HT, HW - 1, HH - 1)
    wall_bricks(d, 0, 0, HT - 1, HH - 1)
    wall_bricks(d, HW - HT, 0, HW - 1, HH - 1)
    rect(d, 0, 0, HW - 1, 0, "wall_light")
    rect(d, HT, HT, HW - HT - 1, HT + 1, "shadow")
    rect(d, HT - 1, HT - 1, HW - HT, HT - 1, "outline")
    rect(d, HT - 1, HH - HT, HW - HT, HH - HT, "outline")
    rect(d, HT - 1, HT - 1, HT - 1, HH - HT, "outline")
    rect(d, HW - HT, HT - 1, HW - HT, HH - HT, "outline")
    # ковровая дорожка от входа (клетки 15-16, строки 13-16)
    x0, y0, x1, y1 = cell(15, 13, 2, 4)
    rect(d, x0, y0, x1, y1, "rug")
    rect(d, x0 + 2, y0 + 2, x1 - 2, y1, "rug_edge")
    rect(d, x0 + 4, y0 + 4, x1 - 4, y1, "rug")
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    # доска в верхней стене: рамка, зелёное поле, записи мелом, полочка
    rect(ld, 160, 1, 380, 13, "board_frame")  # правее шкалы здоровья, она лежит на x 12-309 экрана
    rect(ld, 162, 2, 378, 11, "board")
    for tx, s_ in ((10, "S"), (28, "[a,b]"), (74, "A^B"), (104, "{xn}")):
        text(ld, 160 + tx, 4, s_, "chalk")
    rect(ld, 160, 12, 380, 13, "wood_dark")
    # стол преподавателя [16, 1, 4, 1] под доской: монитор, бумаги, журнал
    x0, y0, x1, y1 = cell(16, 1, 4, 1)
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 1, "wood")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 3, "wood_light")
    rect(ld, x0 + 1, y1 - 2, x1 - 1, y1 - 1, "wood_dark")
    rect(ld, x0 + 9, y0 + 3, x0 + 26, y0 + 9, "monitor")
    rect(ld, x0 + 10, y0 + 4, x0 + 25, y0 + 7, "screen")
    rect(ld, x0 + 36, y0 + 5, x0 + 50, y0 + 11, "paper")
    rect(ld, x0 + 3, y0 + 5, x0 + 6, y0 + 11, "book")
    for cx, cy in HALL_DESKS:
        desk(ld, cx, cy)
    # ящик с бумагами [1, 1, 2, 1] и цветок в горшке [30, 1, 1, 1]
    x0, y0, x1, y1 = cell(1, 1, 2, 1)
    rect(ld, x0 + 1, y0 + 1, x1 - 1, y1 - 1, "box")
    rect(ld, x0 + 1, y0 + 1, x1 - 1, y0 + 3, "wood_light")
    rect(ld, x0 + 13, y0 + 1, x0 + 16, y1 - 1, "wood_dark")
    x0, y0, x1, y1 = cell(30, 1)
    rect(ld, x0 + 3, y0 + 8, x1 - 3, y1 - 1, "pot")
    disc(ld, x0 + 7, y0 + 5, 6, "leaf_dark")
    disc(ld, x0 + 6, y0 + 4, 4, "leaf")
    lay_on(img, lay)
    # выход сверху и вход снизу: светлые пороги, не затемнены
    doorway(d, img, 26, 0, "door_out", "wood_dark")
    doorway(d, img, 15, HH - HT, "door_in", "wood_dark")
    return finish(img)


def hedge(d, x0, y0, x1, y1):
    """Живая изгородь сверху: тёмная зелень, кусты листвы."""
    rect(d, x0, y0, x1, y1, "leaf_dark")
    for y in range(y0, y1, 6):
        off = 0 if (y // 6) % 2 else 4
        for x in range(x0 + off, x1, 8):
            rect(d, x, y + 1, min(x + 3, x1), min(y + 3, y1), "leaf")


def birch(d, base_d, cx, cy):
    """Берёза сверху: неровная светлая крона в верхней части клетки 2x2, под ней длинный
    белый ствол с чёрными чёрточками коры (как на фото)."""
    x0, y0, x1, y1 = cell(cx, cy, 2, 2)
    mx, my = (x0 + x1) // 2, (y0 + y1) // 2
    disc(base_d, mx + 3, my + 3, 10, "shadow_ground")
    for ox in (-7, 7):  # поникшие боковые клочья
        disc(d, mx + ox, my - 1, 4, "birch_dark")
    disc(d, mx, my - 5, 10, "birch_dark")
    disc(d, mx - 2, my - 7, 7, "birch")
    for ox, oy in ((-6, -9), (1, -12), (-8, -3), (3, -5), (6, -9)):
        rect(d, mx + ox, my + oy, mx + ox + 2, my + oy + 1, "birch_light")
    rect(d, mx - 1, my + 3, mx + 1, y1 - 1, "paper")
    for ty in (my + 5, my + 8, my + 11):  # кора — после кроны, чтобы не закрасилась
        rect(d, mx - 1, ty, mx, ty, "outline")


def flag(d, cx, cy, stripes, left):
    """Флагшток: основание в клетке (cx, cy), шест и полотнище (наружу от входа) поднимаются
    над клеткой и заходят на клетку стены здания выше."""
    x0, y0, x1, y1 = cell(cx, cy)
    rect(d, x0 + 5, y1 - 4, x0 + 9, y1 - 1, "base_dark")
    rect(d, x0 + 7, y0 - 8, x0 + 7, y1 - 3, "step_a")
    fx0 = x0 if left else x0 + 8
    for i, col in enumerate(stripes):
        rect(d, fx0, y0 - 8 + i, fx0 + 6, y0 - 8 + i, col)


# здание: строки 0-5 целиком, кроме дверей [15, 5, 2, 1]; флагштоки по бокам крыльца и берёзы — препятствия
ENTRANCE_WALLS = [[0, 0, 32, 5], [0, 5, 15, 1], [17, 5, 15, 1], [9, 6, 1, 1], [22, 6, 1, 1],
                  [2, 8, 2, 2], [2, 13, 2, 2], [28, 8, 2, 2], [28, 13, 2, 2]]
WIN_ROWS = (40, 52, 64)  # верх окон трёх этажей (половинный холст)
PORTICO = (184, 295)  # козырёк и ниша входа по x: шире центрального блока, как на фото


def window(d, x, wy):
    """Окно 7x7: белая рама, голубое стекло, импост, блик."""
    rect(d, x, wy, x + 6, wy + 6, "paper")
    rect(d, x + 1, wy + 1, x + 5, wy + 5, "glass")
    rect(d, x + 3, wy + 1, x + 3, wy + 5, "paper")
    d.point((x + 1, wy + 1), fill=P["screen"])


def window_row(x0, x1, step):
    """x левых краёв окон шириной 7, ряд по центру отрезка [x0, x1]."""
    n = (x1 - x0 + 1 - 7) // step + 1
    start = x0 + (x1 - x0 + 1 - ((n - 1) * step + 7)) // 2
    return [start + i * step for i in range(n)]


def bg_level3_entrance():
    """Львовка, мирная комната: площадь перед корпусом (по фото: синее левое крыло со светлыми
    поясами, светлое правое крыло с синими простенками, узкий светлый центральный блок с
    пилястрами и белой вывеской, белый козырёк, тёмная ниша с тёмными колоннами, синяя крыша с
    ограждением и фронтонами, флаги по бокам крыльца, широкое крыльцо с пандусами, газоны с берёзами).
    Вход снизу (клетки 15-16), выход — двери корпуса [15, 5, 2, 1]."""
    img = Image.new("RGBA", (HW, HH), P["asphalt"])
    d = ImageDraw.Draw(img)
    # асфальт площади: редкие светлые и тёмные крапинки, пара трещин
    for i in range(0, HW * HH, 97):
        x, y = (i * 37) % HW, (i * 53) % HH
        d.point((x, y), fill=P["asphalt_light"] if i % 2 else P["shadow_ground"])
    for x0, y0 in ((150, 160), (330, 210), (240, 140)):
        for k in range(7):
            d.point((x0 + k, y0 + (k // 2) % 2), fill=P["shadow_ground"])
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    # изгородь по периметру (стена)
    hedge(ld, 0, 0, HT - 2, HH - 1)  # на 1 px уже клетки: контур слоя ляжет внутри стены
    hedge(ld, HW - HT + 1, 0, HW - 1, HH - 1)
    hedge(ld, 0, HH - HT + 1, HW - 1, HH - 1)
    # газоны по бокам с белым бордюром [1, 6, 6, 11] и [25, 6, 6, 11]
    for gx in (1, 25):
        x0, y0, x1, y1 = cell(gx, 6, 6, 11)
        rect(ld, x0, y0, x1, y1, "leaf")
        for tx in range(x0 + 3, x1, 7):
            for ty in range(y0 + 5, y1, 8):
                ld.point((tx + (ty // 8) % 3, ty), fill=P["leaf_dark"])
        ex = x1 - 1 if gx == 1 else x0
        rect(ld, ex, y0, ex + 1, y1, "paper")
        rect(ld, x0, y0 + 1, x1, y0 + 2, "paper")  # строку y0 займёт контур здания
    lay_on(img, lay)
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    # крыша: синий металл с фальцами, конёк, ограждение по краю
    rect(ld, 0, 0, HW - 1, 35, "roof")
    rect(ld, 0, 18, HW - 1, 35, "rail")
    for x in range(4, HW, 8):
        rect(ld, x, 0, x, 16, "roof_dark")
        rect(ld, x, 19, x, 30, "roof")
    rect(ld, 0, 17, HW - 1, 17, "roof_dark")
    rect(ld, 0, 33, HW - 1, 35, "roof_dark")
    rect(ld, 0, 31, HW - 1, 31, "step_b")
    for x in range(2, HW, 6):
        ld.point((x, 32), fill=P["step_a"])
    for gx in (190, 290):  # фронтоны над краями центрального блока (симметрично оси двери 239.5)
        for k in range(8):
            rect(ld, gx - 2 - 2 * k, 24 + k, gx + 1 + 2 * k, 24 + k, "hse_light")
        rect(ld, gx - 2, 26, gx + 1, 28, "glass")
    rect(ld, 0, 36, HW - 1, 37, "paper")  # белый карниз
    # левое крыло: синее, светлые пояса между этажами
    rect(ld, 0, 38, 189, 77, "hse_blue")
    for y in (48, 60):
        rect(ld, 0, y, 189, y + 2, "hse_band")
    for wy in WIN_ROWS:
        for x in window_row(2, 187, 13):
            window(ld, x, wy)
    # правое крыло: светлое, синие простенки между колонками окон, синяя полоса под карнизом
    rect(ld, 290, 38, HW - 1, 77, "hse_light")
    rect(ld, 290, 38, HW - 1, 39, "hse_blue")
    cols = window_row(292, 477, 13)
    for x in cols[:-1]:
        rect(ld, x + 8, 38, x + 11, 77, "hse_blue")
    for wy in WIN_ROWS:
        for x in cols:
            window(ld, x, wy)
    # центральный блок: светлый, 5 окон с белыми пилястрами между ними
    rect(ld, 190, 38, 289, 77, "hse_light")
    for x in (193, 211, 229, 247, 265, 284):  # посередине между окнами, симметрично оси двери
        rect(ld, x, 38, x + 1, 77, "paper")
        rect(ld, x + 2, 38, x + 2, 77, "hse_band")
    for wy in WIN_ROWS[:2]:  # нижний этаж закрыт козырьком и нишей входа
        for x in (200, 218, 236, 254, 272):
            window(ld, x, wy)
    # главная вывеска: белая плита с тёмно-синими «буквами» (без эмблемы)
    rect(ld, 194, 47, 285, 51, "paper")
    rect(ld, 194, 47, 285, 47, "outline")
    rect(ld, 194, 51, 285, 51, "outline")
    x = 206  # 21 «буква» по 3 px и 2 пробела = 68 px, по центру плиты 194-285
    for word in (7, 5, 9):
        for _ in range(word):
            rect(ld, x, 48, x + 1, 50, "hse_blue_dark")
            x += 3
        x += 3
    # цоколь: белая полоса и тёмный кирпич. Слой здания кончается на y = 88, чтобы его контур
    # лёг в строку 89 — ещё внутри клеток стены (строка 5), а не на проходимую строку 6
    rect(ld, 0, 78, HW - 1, 78, "paper")
    rect(ld, 0, 79, HW - 1, 88, "brick")
    for y in (82, 85, 88):
        rect(ld, 0, y, HW - 1, y, "brick_dark")
        for x in range((y // 3) % 2 * 4, HW, 8):
            ld.point((x, y - 1), fill=P["brick_dark"])
    for x in (188, 291):  # водосточные трубы на стыках центрального блока с крыльями, до земли
        rect(ld, x, 36, x, 88, "rail")
    # вход: портик шире центрального блока (как на фото), тёмная остеклённая ниша, тёмные
    # гранитные колонны, двери, белый козырёк с плашкой
    px0, px1 = PORTICO
    rect(ld, px0, 67, px1, 88, "door_glass")
    for x in (224, 239, 240, 255):
        rect(ld, x, 67, x, 74, "base_dark")
    x0, y0, x1, y1 = cell(15, 5, 2, 1)
    rect(ld, x0, y0, x1, y1 - 1, "door_out")
    for x in (188, 200, 212, 264, 276, 288):
        rect(ld, x, 67, x + 3, 88, "base_dark")
        rect(ld, x + 3, 67, x + 3, 88, "brick")
    rect(ld, px0, 60, px1, 66, "paper")
    rect(ld, px0, 66, px1, 66, "step_b")
    rect(ld, px0 + 6, 62, px1 - 6, 64, "hse_blue_dark")
    for x in range(px0 + 9, px1 - 8, 4):
        rect(ld, x, 63, x + 1, 63, "paper")
    lay_on(img, lay)
    # крыльцо: три широкие ступени [12, 6, 8, 1], пандусы с синими перилами [10, 6, 2, 1] и [20, 6, 2, 1]
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = cell(12, 6, 8, 1)
    for k, col in enumerate(("step_a", "step_b", "step_a")):
        rect(ld, x0, y0 + 5 * k, x1, y0 + 5 * k + 4, col)
    for rx in (10, 20):
        x0, y0, x1, y1 = cell(rx, 6, 2, 1)
        rect(ld, x0, y0, x1, y1, "path")
        rect(ld, x0, y0, x1, y0, "rail")
        rect(ld, x0 if rx == 10 else x1, y0, x0 if rx == 10 else x1, y1, "rail")
    lay_on(img, lay)
    # флаги по бокам крыльца (полотнища наружу) и берёзы — своим слоем, чтобы у полотнищ был контур
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    flag(ld, 9, 6, ("paper", "paper", "rail", "rail", "book", "book"), left=True)
    flag(ld, 22, 6, ("hse_blue_dark", "hse_blue_dark", "paper", "paper", "hse_blue_dark", "hse_blue_dark"), left=False)
    for bx, by in ((2, 8), (2, 13), (28, 8), (28, 13)):
        birch(ld, d, bx, by)
    lay_on(img, lay)
    arrow(img, 16 * HT, 82)
    doorway(d, img, 15, HH - HT, "door_in", "leaf_dark")
    for x in (224, 255):  # чистые края проёма: без обрезков кустов
        rect(d, x, HH - HT, x, HH - 1, "outline")
    return finish(img)


# ---------------------------------------------------------------- шкала здоровья
HP_MAX = 5  # settings.PLAYER_MAX_HEALTH
HP_W, HP_H = 320, 44  # холст с запасом под тряску
HP_X, HP_Y = 10, 7  # где на холсте лежит сама шкала 300x30

# зачётка слева от шкалы: красная обложка с белой этикеткой, на этикетке оценка. 5 жизней = 5 делений,
# оценка от 10 до 0 с шагом 2: жизни 5/4/3/2/1/0 -> 10/8/6/4/2/0. Сетка 11x13 (контур добавляет stamp)
GRADE = {5: "10", 4: "8", 3: "6", 2: "4", 1: "2", 0: "0"}
GRADE_COLOR = {5: "bar_green_dark", 4: "bar_green_dark", 3: "bar_yellow_dark", 2: "bar_orange_dark",
               1: "bar_red_dark", 0: "bar_red_dark"}
BOOK = [  # раскрытая зачётка сверху: красная обложка по краю, две страницы, корешок посередине, срез страниц внизу
    "RRRRRRRRRRRRR",
    "RWWWWsWWWWWWR",
    "RWWWWsWWWWWWR",
    "RWWWWsWWWWWWR",
    "RWWWWsWWWWWWR",
    "RWWWWsWWWWWWR",
    "RWWWWsWWWWWWR",
    "RWWWWsWWWWWWR",
    "RWWWWsWWWWWWR",
    "RWWWWsWWWWWWR",
    "RWWWWsWWWWWWR",
    "RttttsttttttR",
    "RRRRRRRRRRRRR",
]
DIGIT = {"0": ["###", "#.#", "#.#", "#.#", "###"], "1": ["#", "#", "#", "#", "#"], "2": ["##.", "..#", ".#.", "#..", "###"],
         "4": ["#.#", "#.#", "###", "..#", "..#"], "6": [".##", "#..", "###", "#.#", "###"],
         "8": ["###", "#.#", "###", "#.#", "###"]}  # узкая единица, чтобы «10» влезло на правую страницу (6 px)


def hp_book(img, n, hit=False):
    """Раскрытая зачётка слева от шкалы: на левой странице строчки, на правой оценка.
    n = текущее здоровье 0..5, hit = кадр попадания (обложка светлеет)."""
    cover = "hit_red_light" if hit else ("book" if n > 0 else "face_dead")
    stamp(img, BOOK, 1, 1, {"R": cover, "s": "step_b", "W": "paper", "t": "step_b"})
    px = img.load()
    for y, x1 in ((3, 5), (5, 4), (7, 5), (9, 3)):  # записи на левой странице
        for x in range(2, x1 + 1):
            px[x, y] = P["step_b"] + (255,)
    for x in range(8, 12):  # подпись на правой странице
        px[x, 10] = P["step_b"] + (255,)
    grade = GRADE[n]
    x = 7 if len(grade) == 2 else 8  # правая страница шире левой: x 7..12
    for ch in grade:
        for j, row in enumerate(DIGIT[ch]):
            for i, c in enumerate(row):
                if c == "#":
                    px[x + i, 4 + j] = P[GRADE_COLOR[n]] + (255,)
        x += len(DIGIT[ch][0]) + 1


def hp_color(n):
    return {5: "bar_green", 4: "bar_green", 3: "bar_yellow", 2: "bar_orange"}.get(n, "bar_red")


def hp_bar(n, frac=None, hit=False, dx=0, dy=0, flash=False):
    """Кадр шкалы на холсте 320x44. n = жизни 0..5, frac = доля заливки, dx/dy = сдвиг тряски."""
    frac = n / HP_MAX if frac is None else frac
    layer = Image.new("RGBA", (150, 15), (0, 0, 0, 0))  # половинное разрешение, потом x2
    d = ImageDraw.Draw(layer)
    x0, x1, y0, y1 = 16, 149, 2, 12
    rect(d, x0, y0, x1, y1, "hit_red" if flash else "outline")
    rect(d, x0 + 1, y0 + 1, x1 - 1, y1 - 1, "hit_back" if flash else "bar_back")
    rect(d, x0 + 1, y1 - 2, x1 - 1, y1 - 1, "hit_red_light" if flash else "path")
    inner = x1 - 1 - (x0 + 1)
    fw = int(round((inner + 1) * max(0.0, min(1.0, frac))))
    if fw > 0:
        col = "hit_red" if flash else hp_color(n)  # заливка, блик сверху (_light), тень снизу (_dark)
        rect(d, x0 + 1, y0 + 1, x0 + fw, y1 - 1, col)
        rect(d, x0 + 1, y0 + 1, x0 + fw, y0 + 2, col + "_light")
        rect(d, x0 + 1, y1 - 2, x0 + fw, y1 - 1, col + "_dark")
    for i in range(1, HP_MAX):  # деления: одна жизнь = одна секция
        sx = x0 + 1 + (inner + 1) * i // HP_MAX
        rect(d, sx, y0 + 1, sx, y1 - 1, "outline")
    hp_book(layer, n, hit)
    layer = layer.resize((300, 30), Image.NEAREST)
    out = Image.new("RGBA", (HP_W, HP_H), (0, 0, 0, 0))
    out.paste(layer, (HP_X + dx, HP_Y + dy), layer)
    return out


# кадр попадания: (сдвиг x, сдвиг y, красная вспышка, лицо «ай»)
HIT_FRAMES = [(8, -4, True, True), (-8, 4, False, True), (6, -2, True, True),
              (-4, 2, False, True), (2, 0, True, True), (0, 0, False, False)]


def save_hp_bars():
    for n in range(HP_MAX + 1):
        save(hp_bar(n), "ui_health_%d" % n)
    save(hp_bar(HP_MAX), "ui_health_bar")
    for n in range(HP_MAX):  # попадание: было n+1, стало n
        old, new = (n + 1) / HP_MAX, n / HP_MAX
        for k, (dx, dy, flash, hit) in enumerate(HIT_FRAMES, 1):
            frac = old + (new - old) * min(1.0, k / 4)
            save(hp_bar(n, frac, hit=hit, dx=dx, dy=dy, flash=flash), "ui_health_hit_%d_%d" % (n, k))


# ---------------------------------------------------------------- персонажи, 8 сторон
# Попиксельный пиксель-арт: каждая деталь — сетка символов, один символ = один пиксель.
# Вид сверху, чиби (большая голова). Персонаж собирается из деталей (рюкзак, ноги, корпус,
# руки, голова), у каждой детали свой контур 1 px. Босс рисуется в той же сетке 32x32 и
# увеличивается в 2 раза. Виды w, sw, nw — отражение e, se, ne, но руки расставлены
# отдельно: у героя зачётка всегда в левой руке, стреляет правой; у препода мел и
# стрельба — левая рука.

# Легенда сеток: . прозрачно, a — тень под ногами (чёрная, альфа 60). Общие символы ниже:
# K/E контур/зрачок, S/s кожа/тень, M рот, W бумага, R красное, L стекло очков, C мел.
# H/h/d (волосы), T/t (одежда), P/p (ближняя/дальняя штанина), O (обувь), Y/y (рюкзак),
# m (усы), F (кончик пальца или мел) задаёт персонаж в CHARS[...]["pal"]
COMMON = {"K": "outline", "E": "outline", "S": "skin", "s": "skin_dark", "M": "mouth",
          "W": "paper", "R": "book", "L": "lens", "C": "chalk"}

HEAD_S = [
    ".....HHHHHHHH.....",
    "...HHHhhhhHHHHH...",
    "..HHhhhhhHHHHHHH..",
    ".HHHhhhHHHHHHHHHH.",
    ".HHHHHHHHHHHHHHHd.",
    "HHHHHHHHHHHHHHHHdd",
    "HHHHHHHHHHHHHHHHdd",
    "HdHHHHHHHHHHHHHHdd",
    "HdHSSHHSSSSHHSSHdd",
    "HdSSSSSSSSSSSSSSdd",
    "HdSSKKSSSSSSKKSSdd",
    ".dSSKKSSSSSSKKSSd.",
    ".dSsSSMSSSSMSSsSd.",
    "..SSSSSMMMMSSSSS..",
    "...ssssssssssss...",
]
HEAD_SE = [
    ".....HHHHHHHH.....",
    "...HHhhhhHHHHHH...",
    "..HhhhhhHHHHHHHH..",
    ".HHhhhHHHHHHHHHHH.",
    ".dHHHHHHHHHHHHHHH.",
    "ddHHHHHHHHHHHHHHHH",
    "ddHHHHHHHHHHHHHHHH",
    "ddHHHHHHHHHHHHHHHH",
    "ddHHHHSHHSSSSHHSSH",
    "ddHHSSSSSSSSSSSSSS",
    "ddHsSSSSKKSSSSKKSS",
    ".dHsSSSSKKSSSSKKS.",
    ".dHSSSSsSMSSSSMsS.",
    "..HSSSSSSSMMMMSSS.",
    "...dssssssssssss..",
]
HEAD_E = [
    "....HHHHHHH.....",
    "..HHHhhhhHHHH...",
    ".HHHhhhhhhHHHH..",
    ".HHHHHhhhHHHHHH.",
    "dHHHHHHHHHHHHHHH",
    "dHHHHHHHHHHHHHHH",
    "dHHHHHHHHHHHHHHH",
    "ddHHHHHHHHHHHHHH",
    "ddHHHHHHHHHHSHSS",
    "ddHHHHHHHSSSSSSS",
    "ddHHHHsSSSSSSKSS",
    "ddHHHHsSSSSSSKSS",
    ".ddHHHSSSSSSSSSS",
    "..ddHSSSSSSSSMMS",
    "...ddsssssssss..",
]
HEAD_N = [
    ".....HHHHHHHH.....",
    "...HHHhhhhHHHHH...",
    "..HHhhhhhhHHHHHH..",
    ".HHHhhhhHHHHHHHHH.",
    ".HHHHhhHHHHHHHHHd.",
    "HHHHHHHHHHHHHHHHdd",
    "HHHHHHHHHHHHHHHHdd",
    "HdHHHHHHHHHHHHHHdd",
    "HdHHHHHHHHHHHHHHdd",
    "SdHHHHHHHHHHHHHHdS",
    "SddHHHHHHHHHHHHddS",
    ".dddHHHHHHHHHHddd.",
    ".ddddHHHHHHHHdddd.",
    "..dddddddddddddd..",
    "...ssssssssssss...",
]
HEAD_NE = HEAD_N[:9] + [
    "HdHHHHHHHHHHHHHdsS",
    "HddHHHHHHHHHHHHdSS",
    ".dddHHHHHHHHHHddS.",
    ".ddddHHHHHHHHddss.",
    "..ddddddddddddss..",
    "...ssssssssssss...",
]
# препод: седая шевелюра, очки (оправа, светлые стёкла, зрачки, перемычка, дужки), усы
BOSS_S = [
    "....HHhHHHHhHH....",
    "..HHhhhHHHHhhhHH..",
    ".HHhhhhhHHhhhhhHH.",
    "HHHhhhHHHHHHhhHHHH",
    "HHHHHHHHHHHHHHHHHd",
    "HHHHHHHHHHHHHHHHdd",
    "HdHHHHHHHHHHHHHHdd",
    "HdHSSSSSSSSSSSSHdd",
    "HdSSSSSSSSSSSSSSdd",
    "HdSKKKKKSSKKKKKSdd",
    "HdKKLELKKKKLELKKdd",
    "HdSKKKKKSSKKKKKSdd",
    "HdSSSSSSSSSSSSSSdd",
    ".dSSSSmmmmmmSSSSd.",
    "..ssssssMMssssss..",
]
BOSS_SE = [
    "....HHhHHHHhHH....",
    "..HHhhhHHHHhhhHH..",
    ".HHhhhhhHHhhhhhHH.",
    "HHHhhhHHHHHHhhHHHH",
    "dHHHHHHHHHHHHHHHHH",
    "ddHHHHHHHHHHHHHHHH",
    "ddHHHHHHHHHHHHHHHH",
    "ddHHHSSSSSSSSSSSSH",
    "ddHsSSSSSSSSSSSSSS",
    "ddHsSKKKKKSKKKKKSS",
    "ddHKKKLELKKKLELKSS",
    "ddHsSKKKKKSKKKKKSS",
    ".dHSSSSSSSSSSSSSS.",
    "..dSSSSSmmmmmmSSS.",
    "...ssssssMMssssss.",
]
BOSS_E = [
    "...HHhHHHHhH....",
    ".HHhhhHHHhhhHH..",
    "HHhhhhhHHhhhhHH.",
    "HHHhhHHHHHHhhHHH",
    "dHHHHHHHHHHHHHHH",
    "dHHHHHHHHHHHHHHH",
    "ddHHHHHHHHHHHHHH",
    "ddHHHHHHHHSSSSSS",
    "ddHHHHHsSSSSSSSS",
    "ddHHHHHsSSKKKKSS",
    "ddHHHHHKKKKLEKSS",
    "ddHHHHHsSSKKKKSS",
    ".dHHHHSSSSSSSSSS",
    "..dHHSSSSSSSmmmm",
    "...ddssssssssMs.",
]
BOSS_N = [  # со спины — шевелюра прядями, не лысина
    "....HHhHHHHhHH....",
    "..HHhhhHHHHhhhHH..",
    ".HHhhhhhHHhhhhhHH.",
    "HHHhhhHHhhHHhhHHHH",
    "HHHHHHhhhHHHHHHHHd",
    "HHhhHHHHHHHhhHHHdd",
    "HdhhhHHHhhHHHHHHdd",
    "HdHHHHhhhHHHhhHHdd",
    "HdHHHHHHHHHHHHHHdd",
    "SdHHhHHHHHHhHHHHdS",
    "SddHHHHHHHHHHHHddS",
    ".dddHHdHHHHdHHddd.",
    ".ddddHHHHHHHHdddd.",
    "..dddddddddddddd..",
    "...ssssssssssss...",
]
BOSS_NE = BOSS_N[:9] + HEAD_NE[9:]
HEADS = {
    "player": {"s": HEAD_S, "se": HEAD_SE, "e": HEAD_E, "ne": HEAD_NE, "n": HEAD_N},
    "boss": {"s": BOSS_S, "se": BOSS_SE, "e": BOSS_E, "ne": BOSS_NE, "n": BOSS_N},
}
TORSOS = {
    "player": {  # бирюзовая куртка с молнией, лямки рюкзака; со спины — рюкзак
        "s": ["TTTYTTtTYTTT", "TTTyTTtTyTTT", "TTTTTTtTTTTT", "tttttttttttt"],
        "se": ["TTTTYTTtTYTT", "TTTTyTTtTyTT", "TTTTTTTtTTTT", "tttttttttttt"],
        "e": ["TYTTTTtT", "TYTTTTtT", "TyTTTTtT", "tttttttt"],
        "ne": ["TYYYYYYYYYTT", "TYyyyyyyyYTT", "TYYYYYYYYYTT", "tyyyyyyyyytt"],
        "n": ["TYYYYYYYYYYT", "TYYyyyyyyYYT", "TYYYYYYYYYYT", "tyyyyyyyyyyt"],
    },
    "boss": {  # пиджак, рубашка, галстук; со спины — шов
        "s": ["TTTtWRRWtTTT", "TTTtWRRWtTTT", "TTTTtRRtTTTT", "tttttttttttt"],
        "se": ["TTTTtWRRWtTT", "TTTTtWRRWtTT", "TTTTTtRRtTTT", "tttttttttttt"],
        "e": ["TTTTTTWR", "TTTTTTWR", "TTTTTTTR", "tttttttt"],
        "ne": ["TTTTttTTTTTT", "TTTTttTTTTTT", "TTTTttTTTTTT", "tttttttttttt"],
        "n": ["TTTTTttTTTTT", "TTTTTttTTTTT", "TTTTTttTTTTT", "tttttttttttt"],
    },
}
PACK_TOP = ["YYYYYYYYYYYY", "YYYyyyyyyYYY", "YYYYYYYYYYYY", "yyyyyyyyyyyy", "yyyyyyyyyyyy"]
PACK_SIDE = ["YYYYY", "YYYYY", "YyyyY", "YYYYY", "YYYYY", "YYYYY", "yyyyy", "yyyyy"]
LEG_F = ["PPPP", "PPPP", "OOOO", "OOOO"]
LEG_NEAR = ["PPP.", "PPP.", "PPP.", "OOOO"]
LEG_FAR = ["ppp.", "ppp.", "ppp.", "OOOO"]
SHADOW = ["..aaaaaaaaaa..", "aaaaaaaaaaaaaa", "..aaaaaaaaaa.."]

ARM_HANG = ["TTT", "TTT", "ttt", "SSS", "SSS"]
SLEEVE = ["ttt", "ttt", "ttt", "SSS"]  # в профиль рука без контура, рукав темнее куртки
ITEMS = {
    "book": dict(  # зачётка: красная обложка, снизу край страниц
        arm=["TTT....", "TTTRRRR", "tttRRRR", "SSSRRRR", "SSSRRRR", "...WWWW"],
        far=(["RRRR", "RRRR", "RRRR", "WWWW"], 19, 22),
        near=(["RRRR", "RRRR", "RRRR", "RRRR", "WWWW"], 12, 22)),
    "chalk": dict(
        arm=["TTT....", "TTT....", "ttt....", "SSSC...", "SSSC...", "...C..."],
        far=None,
        near=(["CCC"], 12, 24)),
}
# стреляющая рука, F — кончик пальца («пистолет») или мел
G_DOWN = ["TTT", "TTT", "TTT", "ttt", "SSS", "SSS", ".F."]
G_UP = [".F.", "SSS", "SSS", "TTT", "TTT", "TTT", "TTT", "TTT"]
G_RIGHT = ["TTTTTTSS.", "TTTTTTSSF", "ttttttSS."]
G_DR = ["TTT....", "TTTT...", ".TTTT..", "..TTSS.", "...SSSS", ".....FF"]
G_OVER = [  # nw: рука поднята из-за головы вверх-влево, нижнюю часть закрывает голова
    "FF................",
    "SSSTT.............",
    ".SSTTTTTT.........",
    "....TTTTTTTTT.....",
    ".......ttTTTTTT...",
    "...........TTTTTT.",
    ".............TTTTT",
]

CHARS = {
    "player": dict(scale=1, dy=1, head="player", torso="player", item="book", gun="right", pack=True,
                   pal={"H": "hair", "h": "hair_light", "d": "hair_dark", "T": "teal", "t": "teal_dark",
                        "P": "pants", "p": "pants_dark", "O": "shoe", "Y": "pack", "y": "pack_dark",
                        "F": "skin"}),
    "boss_level3": dict(scale=2, dy=-1, head="boss", torso="boss", item="chalk", gun="left", pack=False,
                        pal={"H": "hair_grey", "h": "paper", "d": "hair_grey_dark", "m": "hair_grey_dark",
                             "T": "jacket", "t": "jacket_dark", "P": "boss_pants", "p": "boss_pants_dark",
                             "O": "boss_shoe", "F": "chalk"}),
}
DIRS = ["s", "se", "e", "ne", "n", "nw", "w", "sw"]
MIRROR = {"s": "s", "se": "sw", "e": "w", "ne": "nw", "n": "n", "nw": "ne", "w": "e", "sw": "se"}
BASE = {"s": "s", "se": "se", "sw": "se", "e": "e", "w": "e", "ne": "ne", "nw": "ne", "n": "n"}
AIM = {"s": (0, 1), "se": (1, 1), "e": (1, 0), "ne": (1, -1), "n": (0, -1), "nw": (-1, -1), "w": (-1, 0), "sw": (-1, 1)}

# висящие руки: (деталь, x, y, слой). back — за корпусом, front — перед ним
ARMS = {
    "s": {"right": ("hang", 7, 21, "front"), "left": ("item", 22, 21, "front")},
    "se": {"right": ("hang", 7, 21, "front"), "left": ("item", 21, 21, "back")},
    "sw": {"right": ("hang", 7, 21, "back"), "left": ("item", 22, 21, "front")},
    "n": {"right": ("hang", 22, 21, "front"), "left": ("item_b", 3, 21, "front")},
    "ne": {"right": ("hang", 22, 21, "front"), "left": ("item_b", 4, 21, "back")},
    "nw": {"right": ("hang", 22, 21, "back"), "left": ("item_b", 3, 21, "front")},
    "e": {"right": ("sleeve", 14, 21, "front"), "left": ("far", 0, 0, "back")},
    "w": {"right": None, "left": ("near", 15, 21, "front")},
}
# стреляющая правая рука: (сетка, x, y, слой); top — поверх головы, under_head — под ней
GUN_RIGHT = {
    "s": (G_DOWN, 7, 21, "front"),
    "se": (G_DR, 15, 21, "front"),
    "e": (G_RIGHT, 15, 21, "front"),
    "ne": (G_DR[::-1], 21, 16, "top"),
    "n": (G_UP, 24, 13, "top"),
    "nw": (G_OVER, 3, 3, "under_head"),
    "w": ([r[::-1] for r in G_RIGHT], 8, 21, "back"),
    "sw": ([r[::-1] for r in G_DR], 3, 21, "back"),
}

# (левая нога, правая нога, левая рука, правая рука, подъём корпуса)
IDLE = [(0, 0, 0, 0, 0), (0, 0, 0, 0, -1)]
WALK = [(1, -1, -1, 1, 0), (0, 0, 0, 0, 1), (-1, 1, 1, -1, 0), (0, 0, 0, 0, 1)]
STAND = (0, 0, 0, 0, 0)


def mirror(grid):
    return [row[::-1] for row in grid]


def stamp(img, grid, x, y, pal, line=True):
    """Деталь по сетке символов; line — свой контур 1 px вокруг детали."""
    px = img.load()
    w, h = img.size
    cells = [(x + i, y + j, ch) for j, row in enumerate(grid) for i, ch in enumerate(row) if ch != "."]
    own = {(a, b) for a, b, _ in cells}
    if line:
        for a, b, _ in cells:
            for q in ((a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)):
                if q not in own and 0 <= q[0] < w and 0 <= q[1] < h:
                    px[q] = P["outline"] + (255,)
    for a, b, ch in cells:
        if 0 <= a < w and 0 <= b < h:
            px[a, b] = (0, 0, 0, 60) if ch == "a" else P[pal.get(ch) or COMMON[ch]] + (255,)


def gun_spec(hand, dname):
    if hand == "right":
        return GUN_RIGHT[dname]
    grid, x, y, layer = GUN_RIGHT[MIRROR[dname]]  # левша: зеркало правой руки
    return mirror(grid), 32 - x - len(grid[0]), y, layer


def draw_slash(img, dname, radius, y0):
    """Дуга удара перед бойцом: белые пиксели по дуге ±45° от направления удара."""
    ax, ay = AIM[dname]
    ang = math.atan2(ay, ax)
    px = img.load()
    for off in range(-45, 46, 9):
        a = ang + math.radians(off)
        for r in (radius, radius + 1):
            x, y = round(16 + r * math.cos(a)), round(16 + y0 + r * math.sin(a) * 0.9)
            if 1 <= x <= 30 and 1 <= y <= 30:
                px[x, y] = P["paper"] + (255,)


# фазы ударов: (левая нога, правая нога, левая рука, правая рука, подъём корпуса)
ATK_WINDUP = (0, 0, -1, -1, -1)
ATK_STRIKE = (0, 0, 1, 1, 0)
LUNGE = {"windup": -1, "strike": 2}  # сдвиг верхней части тела вдоль направления удара, px


def character(name, dname, ph, shoot=None, atk=None, beak=False):
    """Кадр персонажа. shoot: None, "aim" (рука вытянута) или "recoil" (отдача).
    atk (ближний бой): None, "windup" (замах: рука отведена, корпус назад) или "strike" (удар: выпад
    вперёд, рука вытянута, дуга удара)."""
    c = CHARS[name]
    pal = c["pal"]
    lx = ly = 0
    if atk:
        ax_, ay_ = AIM[dname]
        lx, ly = ax_ * LUNGE[atk], ay_ * LUNGE[atk]
        if c["gun"]:
            shoot = "pull" if atk == "windup" else "aim"
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    ll, rl, al, ar, bob = ph
    u = -bob
    base = BASE[dname]
    flip = base != dname
    side = base == "e"
    front = base in ("s", "se")
    item = ITEMS[c["item"]]

    y0 = c["dy"]  # сдвиг фигуры в кадре: герою запас сверху под рюкзак, препода (без рюкзака) — по центру

    def put(grid, x, y, line=True, body=True):
        stamp(img, grid, x + (lx if body else 0), y + y0 + (u + ly if body else 0), pal, line)

    def put_m(grid, x, y, line=True, body=True):  # деталь базового вида, отражённая для w/sw/nw
        if flip:
            grid, x = mirror(grid), 32 - x - len(grid[0])
        put(grid, x, y, line, body)

    def arms(layer):
        for hand, swing in (("right", ar), ("left", al)):
            spec = ARMS[dname][hand]
            if spec is None or spec[3] != layer or (shoot and hand == c["gun"]):
                continue
            kind, x, y, _ = spec
            if kind == "hang":
                put(ARM_HANG, x, y + swing)
            elif kind == "item":
                put(item["arm"], x, y + swing)
            elif kind == "item_b":
                put(mirror(item["arm"]), x, y - swing)
            elif kind == "sleeve":
                put(SLEEVE, x + swing, y, line=False)
            elif kind == "far" and item["far"]:
                g, fx, fy = item["far"]
                put(g, fx, fy)
            elif kind == "near":
                put(SLEEVE, x - swing, y, line=False)
                g, nx, ny = item["near"]
                put(g, nx - swing, ny)

    def gun(layer):
        if not shoot:
            return
        grid, x, y, lay = gun_spec(c["gun"], dname)
        if lay != layer:
            return
        if shoot in ("recoil", "pull"):
            ax, ay = AIM[dname]
            k = 1 if shoot == "recoil" else 2  # "pull": рука отведена назад сильнее, чем при отдаче
            x, y = x - ax * k, y - ay * k
        put(grid, x, y)

    stamp(img, SHADOW, 9, 28 + y0, pal, line=False)
    if c["pack"]:
        if front:
            put_m(PACK_TOP, 10 if base == "s" else 8, 1)
        elif side:
            put_m(PACK_SIDE, 6, 16)
    leg_f, leg_near, leg_far = c.get("legs", (LEG_F, LEG_NEAR, LEG_FAR))
    lxs = c.get("legs_x", (11, 17))
    lline = c.get("legs_line", True)
    if side:  # ноги в профиль: шаг вперёд-назад, дальняя нога темнее
        put_m(leg_far, 12 + 2 * rl, 25, line=lline, body=False)
        put_m(leg_near, 15 + 2 * ll, 25, line=lline, body=False)
    else:
        put(leg_f, lxs[0], 25 + (rl if front else -ll), line=lline, body=False)
        put(leg_f, lxs[1], 25 + (ll if front else -rl), line=lline, body=False)
    arms("back")
    gun("back")
    torso = TORSOS[c["torso"]][base]
    put_m(torso, 12 if side else 10, 21)
    arms("front")
    gun("front")
    gun("under_head")
    head = HEADS[c["head_open"] if beak and c.get("head_open") else c["head"]][base]
    put_m(head, 8 if side else 7, 5 - max(0, len(head) - 15))  # лишние строки сверху: плюмаж, пучок, антенна
    gun("top")
    if atk == "strike" and c.get("slash"):
        draw_slash(img, dname, c["slash"], y0)
    if c["scale"] != 1:
        img = img.resize((32 * c["scale"], 32 * c["scale"]), Image.NEAREST)
    return img


def save_character(name):
    """Покой 2, ходьба 4, стрельба стоя 2, стрельба на ходу 4 кадра на каждое из 8 направлений."""
    for dr in DIRS:
        for k, ph in enumerate(IDLE, 1):
            save(character(name, dr, ph), "%s_idle_%s_%d" % (name, dr, k))
        for k, ph in enumerate(WALK, 1):
            save(character(name, dr, ph), "%s_walk_%s_%d" % (name, dr, k))
            save(character(name, dr, ph, shoot="aim"), "%s_walkshoot_%s_%d" % (name, dr, k))
        save(character(name, dr, STAND, shoot="aim"), "%s_shoot_%s_1" % (name, dr))
        save(character(name, dr, STAND, shoot="recoil"), "%s_shoot_%s_2" % (name, dr))
    # статичный кадр: запасной вариант, пока код не подключил анимацию
    save(character(name, "s", IDLE[0]), "player_idle" if name == "player" else name)


# ---------------------------------------------------------------- набор 19 картинок (этап 1)
# Комнаты этого набора: вход снизу (клетки 15-16), выход сверху (клетки 26-27 в классах, 15-16 во дворах и залах).
FONT = {  # шрифт 3x5 для надписей на досках и вывесках, один символ = один пиксель
    "A": [".#.", "#.#", "###", "#.#", "#.#"], "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": [".##", "#..", "#..", "#..", ".##"], "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"], "S": [".##", "#..", ".#.", "..#", "##."],
    "a": ["...", ".##", "#.#", "#.#", ".##"], "d": ["..#", "..#", ".##", "#.#", ".##"],
    "e": ["...", ".##", "###", "#..", ".##"], "f": [".##", "#..", "##.", "#..", "#.."],
    "i": [".#.", "...", ".#.", ".#.", ".#."], "l": ["##.", ".#.", ".#.", ".#.", ".##"],
    "m": ["...", "###", "###", "#.#", "#.#"], "n": ["...", "##.", "#.#", "#.#", "#.#"],
    "o": ["...", ".#.", "#.#", "#.#", ".#."], "p": ["...", "##.", "#.#", "##.", "#.."],
    "r": ["...", ".##", "#..", "#..", "#.."], "t": [".#.", "###", ".#.", ".#.", ".##"],
    "x": ["...", "#.#", ".#.", "#.#", "#.#"], "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"], "5": ["###", "#..", "##.", "..#", "##."],
    "=": ["...", "###", "...", "###", "..."], "-": ["...", "...", "###", "...", "..."],
    "/": ["..#", "..#", ".#.", "#..", "#.."], "[": ["##.", "#..", "#..", "#..", "##."],
    "]": [".##", "..#", "..#", "..#", ".##"], "{": [".##", ".#.", "##.", ".#.", ".##"],
    "}": ["##.", ".#.", ".##", ".#.", "##."], " ": ["..", "..", "..", "..", ".."],
}


def text(d, x, y, s, col):
    """Надпись шрифтом 3x5 (шаг 4 px) на холсте d."""
    for ch in s:
        for j, row in enumerate(FONT[ch]):
            for i, c in enumerate(row):
                if c == "#":
                    d.point((x + i, y + j), fill=P[col])
        x += len(FONT[ch][0]) + 1


def text_width(s):
    return sum(len(FONT[ch][0]) + 1 for ch in s) - 1


def rotate_cw(grid):
    return ["".join(grid[len(grid) - 1 - c][r] for c in range(len(grid))) for r in range(len(grid[0]))]


def doorway_side(d, img, side, cy, col, frame):
    """Проём в боковой стене высотой 2 клетки (строки cy, cy+1): светлый порог, косяки, стрелка вправо."""
    x0 = 0 if side == "L" else HW - HT
    y0 = cy * HT
    rect(d, x0, y0, x0 + HT - 1, y0 + 2 * HT - 1, col)
    rect(d, x0, y0, x0 + HT - 1, y0 + 1, frame)
    rect(d, x0, y0 + 2 * HT - 2, x0 + HT - 1, y0 + 2 * HT - 1, frame)
    stamp(img, rotate_cw(ARROW), x0 + HT // 2 - 3, y0 + HT - 3, {}, line=False)


def room_shell(floor="boards"):
    """Помещение: пол, кирпичные стены в 1 клетку и внутренняя линия outline. Возвращает (img, d)."""
    img = Image.new("RGBA", (HW, HH), P["wall"])
    d = ImageDraw.Draw(img)
    floor_boards(d, HT, HT, HW - HT, HH - HT)
    wall_bricks(d, 0, 0, HW - 1, HT - 1)
    wall_bricks(d, 0, HH - HT, HW - 1, HH - 1)
    wall_bricks(d, 0, 0, HT - 1, HH - 1)
    wall_bricks(d, HW - HT, 0, HW - 1, HH - 1)
    rect(d, 0, 0, HW - 1, 0, "wall_light")
    rect(d, HT, HT, HW - HT - 1, HT + 1, "shadow")
    rect(d, HT - 1, HT - 1, HW - HT, HT - 1, "outline")
    rect(d, HT - 1, HH - HT, HW - HT, HH - HT, "outline")
    rect(d, HT - 1, HT - 1, HT - 1, HH - HT, "outline")
    rect(d, HW - HT, HT - 1, HW - HT, HH - HT, "outline")
    return img, d


def room_doors(img, d, exit_cell=26):
    """Вход снизу (клетки 15-16), выход сверху (клетки exit_cell, +1): идём снизу вверх."""
    doorway(d, img, 15, HH - HT, "door_in", "wood_dark")
    doorway(d, img, exit_cell, 0, "door_out", "wood_dark")


def chalkboard(ld, x0, y0, x1, lines):
    """Доска в верхней стене: рамка, зелёное поле, полочка и надписи мелом [(x, y, строка)]."""
    rect(ld, x0, y0, x1, y0 + 12, "board_frame")
    rect(ld, x0 + 2, y0 + 1, x1 - 2, y0 + 10, "board")
    rect(ld, x0, y0 + 11, x1, y0 + 12, "wood_dark")
    for tx, ty, s in lines:
        text(ld, x0 + tx, y0 + ty, s, "chalk")


def classroom_desks(ld, cells):
    for cx, cy in cells:
        desk(ld, cx, cy)


# Печерка: класс английского на ремонте. Препятствия: 4 парты у стен, учительский стол, мешки с цементом,
# две банки краски, парты под плёнкой, стремянка на полу
YARD_DESKS = [(3, 3), (3, 5), (21, 3), (21, 5)]  # правые парты не над выходом (клетки 26-27)
YARD_WALLS = ([w for x, y in YARD_DESKS for w in ([x, y, 4, 1], [x + 1, y + 1, 2, 1])]
              + [[14, 1, 4, 1], [1, 1, 2, 1], [3, 13, 3, 2], [7, 15, 1, 1], [8, 15, 1, 1],
                 [25, 12, 4, 2], [24, 15, 5, 1]])


def repair_floor(d):
    """Следы ремонта на полу (проходимые): плёнка, извёстка, капли краски. Рисуется до слоя предметов."""
    x0, y0, x1, y1 = cell(9, 11, 5, 4)  # плёнка с заломами
    rect(d, x0, y0, x1, y1, "screen")
    for k in range(0, x1 - x0, 11):
        rect(d, x0 + k, y0, x0 + k + 1, y1, "glass")
    rect(d, x0, y0 + 20, x1, y0 + 21, "glass")
    rect(d, x0, y0, x1, y0, "outline")
    rect(d, x0, y1, x1, y1, "outline")
    rect(d, x0, y0, x0, y1, "outline")
    rect(d, x1, y0, x1, y1, "outline")
    for i in range(0, 1400, 7):  # извёстка и пыль
        px, py = HT + (i * 53) % (HW - 2 * HT), HT + (i * 29) % (HH - 2 * HT)
        d.point((px, py), fill=P["paper"] if i % 3 else P["step_b"])
    for px, py in ((200, 150), (206, 153), (330, 100), (333, 104), (120, 215)):  # капли краски
        rect(d, px, py, px + 1, py + 1, "pack")
    for x in range(HT + 5, HW - HT - 20, 38):  # пыльные следы ботинок по центру
        d.point((x, 128), fill=P["step_b"])


def repair_walls(d):
    """Куски штукатурки сбиты, видна голая кладка."""
    for x0, y0, x1, y1 in ((0, 40, 13, 86), (0, 180, 13, 215), (HW - 14, 190, HW - 1, 232), (430, 0, 462, 13)):
        rect(d, x0, y0, x1, y1, "step_b")
        for k in range(y0 + 4, y1, 6):
            rect(d, x0, k, x1, k, "brick_dark")
        d.point((x0 + 5, y0 + 2), fill=P["outline"])


def bg_level1_yard():
    """Печерка, класс английского на ремонте: доска с фразами всё ещё висит, но вокруг стройматериалы.
    Вход снизу (клетки 15-16), выход сверху (клетки 26-27), центр свободен."""
    img, d = room_shell()
    repair_walls(d)
    repair_floor(d)
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    chalkboard(ld, 160, 1, 380, [(8, 3, "Hello"), (50, 3, "a/an"), (88, 3, "I am"), (130, 3, "-ed")])
    x0, y0, x1, y1 = cell(14, 1, 4, 1)  # учительский стол под доской, на нём каска и бумаги
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 1, "wood")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 3, "wood_light")
    rect(ld, x0 + 1, y1 - 2, x1 - 1, y1 - 1, "wood_dark")
    disc(ld, x0 + 14, y0 + 8, 4, "pack")
    rect(ld, x0 + 10, y0 + 8, x0 + 18, y0 + 9, "pack_dark")
    rect(ld, x0 + 30, y0 + 5, x0 + 50, y0 + 11, "paper")
    rect(ld, x0 + 3, y0 + 5, x0 + 6, y0 + 11, "book")
    classroom_desks(ld, YARD_DESKS)
    x0, y0, x1, y1 = cell(1, 1, 2, 1)  # шкаф с книгами
    rect(ld, x0 + 1, y0 + 1, x1 - 1, y1 - 1, "box")
    rect(ld, x0 + 1, y0 + 1, x1 - 1, y0 + 3, "wood_light")
    for i, col in enumerate(("book", "pack", "screen", "leaf", "book", "pack")):
        rect(ld, x0 + 3 + i * 4, y0 + 6, x0 + 5 + i * 4, y1 - 3, col)
    # мешки с цементом [3, 13, 3, 2]: два ряда, на верхнем лежит третий
    x0, y0, x1, y1 = cell(3, 13, 3, 2)
    for bx, by, bw in ((x0 + 1, y0 + 14, 20), (x0 + 22, y0 + 14, 21), (x0 + 3, y0 + 3, 20), (x0 + 24, y0 + 3, 19)):
        rect(ld, bx, by, bx + bw - 1, by + 12, "step_a")
        rect(ld, bx, by + 9, bx + bw - 1, by + 12, "step_b")
        rect(ld, bx + 4, by + 4, bx + bw - 5, by + 6, "hse_blue_dark")
    # две банки краски [7, 15, 1, 1] и [8, 15, 1, 1]
    for cx, col in ((7, "enemy_orange"), (8, "hse_blue")):
        x0, y0, x1, y1 = cell(cx, 15)
        disc(ld, (x0 + x1) // 2, (y0 + y1) // 2, 6, "step_b")
        disc(ld, (x0 + x1) // 2, (y0 + y1) // 2, 4, col)
    # парты под плёнкой [25, 12, 4, 2]: стопка, накрытая синей плёнкой, торчат ножки
    x0, y0, x1, y1 = cell(25, 12, 4, 2)
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 2, "screen")
    for k in range(6, x1 - x0 - 4, 14):
        rect(ld, x0 + k, y0 + 2, x0 + k + 1, y1 - 2, "glass")
    rect(ld, x0 + 1, y1 - 3, x1 - 1, y1 - 2, "glass")
    rect(ld, x0 + 4, y1 - 1, x0 + 6, y1, "wood_dark")
    rect(ld, x1 - 6, y1 - 1, x1 - 4, y1, "wood_dark")
    # стремянка на полу [24, 15, 5, 1]: два рельса и перекладины
    x0, y0, x1, y1 = cell(24, 15, 5, 1)
    rect(ld, x0 + 1, y0 + 3, x1 - 1, y0 + 5, "pack")
    rect(ld, x0 + 1, y1 - 5, x1 - 1, y1 - 3, "pack")
    for k in range(x0 + 6, x1 - 2, 9):
        rect(ld, k, y0 + 5, k + 1, y1 - 5, "pack_dark")
    x0, y0, x1, y1 = cell(30, 1)
    rect(ld, x0 + 3, y0 + 8, x1 - 3, y1 - 1, "pot")
    disc(ld, x0 + 7, y0 + 5, 6, "leaf_dark")
    disc(ld, x0 + 6, y0 + 4, 4, "leaf")
    lay_on(img, lay)
    room_doors(img, d)
    return finish(img)


# ---------------------------------------------------------------- остальные фоны набора
# Нарастание по уровню: двор (мирная комната) -> комната уровня -> зал босса (самый тревожный, в духе
# экзамена: бланки, таймер, красные отметки; без крови и монстров). Вход снизу, выход сверху.
FONT.update({
    "E": ["###", "#..", "##.", "#..", "###"], "F": ["###", "#..", "##.", "#..", "#.."],
    "L": ["#..", "#..", "#..", "#..", "###"], "M": ["#.#", "###", "###", "#.#", "#.#"],
    "N": ["##.", "#.#", "#.#", "#.#", "#.#"], "O": [".#.", "#.#", "#.#", "#.#", ".#."],
    "P": ["##.", "#.#", "##.", "#..", "#.."], "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."], "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "D": ["##.", "#.#", "#.#", "#.#", "##."], "b": ["#..", "##.", "#.#", "#.#", "##."],
    "2": ["##.", "..#", ".#.", "#..", "###"], "3": ["##.", "..#", ".#.", "..#", "##."],
    "4": ["#.#", "#.#", "###", "..#", "..#"], "6": [".##", "#..", "###", "#.#", "###"],
    "7": ["###", "..#", ".#.", ".#.", ".#."], "8": ["###", "#.#", "###", "#.#", "###"],
    "9": ["###", "#.#", "###", "..#", "##."], ",": ["...", "...", "...", ".#.", "#.."],
    "!": [".#.", ".#.", ".#.", "...", ".#."], "^": ["###", "#.#", "#.#", "#.#", "#.#"],  # ^ = знак ∩
    "(": [".#.", "#..", "#..", "#..", ".#."], ")": [".#.", "..#", "..#", "..#", ".#."],
})
PALETTE.update({
    "yellow_wall": (232, 200, 120), "yellow_wall_dark": (196, 160, 84),
    "sand": (222, 196, 130), "sand_dark": (190, 164, 100),
    "concrete_a": (150, 148, 142), "concrete_b": (136, 134, 128),
    "tech_a": (158, 176, 184), "tech_b": (146, 164, 172),
    "led_amber": (255, 176, 40),
    "dark_a": (82, 70, 96), "dark_b": (72, 60, 86),
    "dark_wall": (50, 40, 66), "dark_wall2": (62, 50, 80),
    "purple": (122, 72, 162), "purple_dark": (82, 46, 112), "purple_light": (166, 116, 204),
    "exam_red": (200, 48, 60),
    "lvov_floor_a": (150, 128, 98), "lvov_floor_b": (138, 118, 90),
})
P = PALETTE


import math


def bricks(d, x0, y0, x1, y1, c1, c2):
    rect(d, x0, y0, x1, y1, c1)
    for y in range(y0 + 4, y1, 5):
        rect(d, x0, y, x1, y, c2)
        off = 0 if (y // 5) % 2 else 5
        for x in range(x0 + off, x1, 10):
            rect(d, x, y - 4, x, y - 1, c2)


def tiles(d, x0, y0, x1, y1, ca, cb, size=10):
    """Плитка: шахматка из квадратов size x size со швом."""
    for ty in range(y0, y1, size):
        for tx in range(x0, x1, size):
            col = ca if ((tx - x0) // size + (ty - y0) // size) % 2 == 0 else cb
            rect(d, tx, ty, min(tx + size - 1, x1 - 1), min(ty + size - 1, y1 - 1), col)


def shell(wall1, wall2, floor_fn, hi="wall_light"):
    """Помещение: кирпичная стена 1 клетка по периметру, внутренняя линия outline, пол floor_fn(d)."""
    img = Image.new("RGBA", (HW, HH), P[wall1])
    d = ImageDraw.Draw(img)
    floor_fn(d)
    for box in ((0, 0, HW - 1, HT - 1), (0, HH - HT, HW - 1, HH - 1), (0, 0, HT - 1, HH - 1), (HW - HT, 0, HW - 1, HH - 1)):
        bricks(d, *box, wall1, wall2)
    rect(d, 0, 0, HW - 1, 0, hi)
    rect(d, HT, HT, HW - HT - 1, HT + 1, "shadow_ground")
    for box in ((HT - 1, HT - 1, HW - HT, HT - 1), (HT - 1, HH - HT, HW - HT, HH - HT),
                (HT - 1, HT - 1, HT - 1, HH - HT), (HW - HT, HT - 1, HW - HT, HH - HT)):
        rect(d, *box, "outline")
    return img, d


def put_door(img, d, exit_cell, frame="wood_dark"):
    doorway(d, img, 15, HH - HT, "door_in", frame)
    doorway(d, img, exit_cell, 0, "door_out", frame)


def dots(d, n, seed, cols, x0=HT, y0=HT, x1=HW - HT, y1=HH - HT):
    """Крапинки на полу (пыль, мусор): n точек, цвет по кругу из cols."""
    for i in range(n):
        d.point((x0 + (i * seed * 37) % (x1 - x0), y0 + (i * seed * 53 + i * i) % (y1 - y0)), fill=P[cols[i % len(cols)]])


def cable(d, pts, col):
    d.line(pts, fill=P[col], width=1)


def rack(ld, cx, cy, cw, ch, seed=0, screen=False):
    """Серверная стойка сверху/спереди: корпус из блоков по 4 px с лампочками. Кратна клеткам."""
    x0, y0, x1, y1 = cell(cx, cy, cw, ch)
    rect(ld, x0 + 1, y0 + 1, x1 - 1, y1 - 1, "monitor")
    rect(ld, x0 + 1, y0 + 1, x1 - 1, y0 + 2, "base_dark")
    for k, y in enumerate(range(y0 + 4, y1 - 3, 5)):
        rect(ld, x0 + 3, y, x1 - 3, y + 3, "brick_dark")
        for j, x in enumerate(range(x0 + 5, x1 - 5, 4)):
            col = ("bar_green_light", "led_amber", "hit_red", "bar_green_light")[(k * 3 + j + seed) % 4]
            ld.point((x, y + 1), fill=P[col])
        rect(ld, x1 - 8, y + 1, x1 - 5, y + 2, "base_dark")
    if screen:
        rect(ld, x0 + 4, y0 + 4, x1 - 4, y0 + 9, "outline")
        text(ld, x0 + 6, y0 + 3, "ERROR", "hit_red")


def pc_desk(ld, cx, cy, screens=2):
    """Компьютерная парта 4x1: два монитора с экранами, клавиатуры; стул 2x1 под ней."""
    x0, y0, x1, y1 = cell(cx, cy, 4, 1)
    rect(ld, x0 + 20, y1 + 2, x1 - 20, y1 + 10, "wall")
    rect(ld, x0 + 20, y1 + 9, x1 - 20, y1 + 10, "wall_dark")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 1, "tech_b")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 3, "paper")
    rect(ld, x0 + 1, y1 - 2, x1 - 1, y1 - 1, "base_dark")
    for k in range(screens):
        mx = x0 + 6 + k * 26
        rect(ld, mx, y0 + 3, mx + 17, y0 + 9, "monitor")
        rect(ld, mx + 1, y0 + 4, mx + 16, y0 + 7, "screen" if (cx + k) % 3 else "bar_green_light")
        rect(ld, mx + 4, y0 + 10, mx + 13, y0 + 10, "paper")


def exam_sheet(ld, x, y, mark=None):
    rect(ld, x, y, x + 8, y + 10, "paper")
    for k in range(2, 9, 3):
        rect(ld, x + 2, y + k, x + 6, y + k, "step_b")
    if mark:
        text(ld, x + 3, y + 5, mark, "exam_red")


def oak(ld, base, cx, cy):
    """Крона дерева сверху в клетке 2x2: тень на земле, тёмная и светлая листва."""
    x0, y0, x1, y1 = cell(cx, cy, 2, 2)
    mx, my = (x0 + x1) // 2, (y0 + y1) // 2
    disc(base, mx + 3, my + 4, 13, "shadow_ground")
    disc(ld, mx, my, 13, "leaf_dark")
    disc(ld, mx - 2, my - 3, 10, "leaf")
    for ox, oy in ((-7, -7), (3, -9), (-9, 1), (5, 2), (-2, 7)):
        rect(ld, mx + ox, my + oy, mx + ox + 2, my + oy + 1, "bar_green_light")


def fence_wall(ld, x0, y0, x1, y1, vertical):
    """Забор по периметру двора: бетонные плиты со столбами."""
    rect(ld, x0, y0, x1, y1, "step_a")
    rect(ld, x0, y0, x1, y1, "step_a")
    if vertical:
        for y in range(y0, y1, 15):
            rect(ld, x0, y, x1, y, "step_b")
            rect(ld, x0, y, x0 + 3, y + 2, "base_dark")
    else:
        for x in range(x0, x1, 15):
            rect(ld, x, y0, x, y1, "step_b")
            rect(ld, x, y0, x + 2, y0 + 3, "base_dark")


def building_top(ld, roof, roof_dark, wall, wall_dark, trim, height=89):
    """Крыша и фасад корпуса сверху (строки 0-5): общий каркас для дворов."""
    rect(ld, 0, 0, HW - 1, 35, roof)
    for x in range(4, HW, 8):
        rect(ld, x, 0, x, 33, roof_dark)
    rect(ld, 0, 33, HW - 1, 35, roof_dark)
    rect(ld, 0, 36, HW - 1, 37, trim)
    rect(ld, 0, 38, HW - 1, 77, wall)
    for y in (48, 60):
        rect(ld, 0, y, HW - 1, y + 1, wall_dark)
    rect(ld, 0, 78, HW - 1, 78, "paper")
    rect(ld, 0, 79, HW - 1, 88, "brick")
    for y in (82, 85, 88):
        rect(ld, 0, y, HW - 1, y, "brick_dark")


def window7(d, x, wy, boarded=False):
    rect(d, x, wy, x + 6, wy + 6, "paper")
    if boarded:
        rect(d, x + 1, wy + 1, x + 5, wy + 5, "wood")
        rect(d, x + 1, wy + 3, x + 5, wy + 3, "wood_dark")
    else:
        rect(d, x + 1, wy + 1, x + 5, wy + 5, "glass")
        rect(d, x + 3, wy + 1, x + 3, wy + 5, "paper")
        d.point((x + 1, wy + 1), fill=P["screen"])


def courtyard_ground(d, ca, cb, seam):
    rect(d, 0, 0, HW - 1, HH - 1, ca)
    for ty in range(0, HH, 30):
        rect(d, 0, ty, HW - 1, ty, seam)
    for tx in range(0, HW, 30):
        rect(d, tx, 0, tx, HH - 1, seam)
    for i in range(0, 900, 7):
        d.point(((i * 37) % HW, (i * 53) % HH), fill=P[cb])


def door_block(ld, img, canopy="paper"):
    """Двери здания в клетках 15-16 строки 5 (светлые, со стрелкой), навес и ступени."""
    rect(ld, 215, 60, 264, 66, canopy)
    rect(ld, 215, 66, 264, 66, "step_b")
    rect(ld, 221, 67, 258, 88, "base_dark")
    rect(ld, 223, 68, 256, 74, "door_glass")
    x0, y0, x1, y1 = cell(15, 5, 2, 1)
    rect(ld, x0, y0, x1, y1 - 1, "door_out")
    rect(ld, 210, 90, 269, 95, "step_a")
    rect(ld, 202, 96, 277, 101, "step_b")


# ---------- двор Печерки
E1_WALLS = [[0, 0, 32, 5], [0, 5, 15, 1], [17, 5, 15, 1], [2, 8, 5, 3], [24, 8, 3, 2], [27, 13, 3, 3],
            [8, 7, 3, 1], [21, 7, 3, 1], [2, 14, 4, 1]]


def bg_entrance_l1():
    """Печерка, мирная комната: двор перед корпусом на ремонте. Строительные леса на левой части фасада,
    бытовка, поддоны с кирпичом, куча песка, красно-белые барьеры и конусы. Вход снизу, выход — двери корпуса."""
    img = Image.new("RGBA", (HW, HH), P["concrete_a"])
    d = ImageDraw.Draw(img)
    courtyard_ground(d, "concrete_a", "concrete_b", "concrete_b")
    rect(d, 14 * HT, 90, 18 * HT - 1, HH - HT - 1, "asphalt")  # проезд от входа к крыльцу
    for y in range(100, HH - HT, 12):
        rect(d, 16 * HT - 1, y, 16 * HT, y + 5, "pack")
    dots(d, 160, 3, ["step_b", "sand_dark"])
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    fence_wall(ld, 0, 0, HT - 2, HH - 1, True)
    fence_wall(ld, HW - HT + 1, 0, HW - 1, HH - 1, True)
    fence_wall(ld, 0, HH - HT + 1, HW - 1, HH - 1, False)
    lay_on(img, lay)
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    building_top(ld, "brick", "brick_dark", "yellow_wall", "yellow_wall_dark", "paper")
    for wy in (40, 52, 64):
        for k, x in enumerate(range(8, HW - 8, 20)):
            if 196 <= x <= 262:
                continue
            window7(ld, x, wy, boarded=(wy == 64 and k % 3 == 1))
    door_block(ld, img)
    lay_on(img, lay)
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    for x in range(6, 196, 24):  # строительные леса на левой части фасада
        rect(ld, x, 38, x + 1, 89, "enemy_orange_dark")
    for y in (46, 62, 78):
        rect(ld, 6, y, 190, y + 1, "wood")
        rect(ld, 6, y + 2, 190, y + 2, "wood_dark")
    for x in range(6, 170, 24):
        for k in range(8):
            ld.point((x + 2 + k * 3, 62 + k * 2 - 14), fill=P["enemy_orange_dark"])
    x0, y0, x1, y1 = cell(2, 8, 5, 3)  # бытовка: синий вагончик с окнами и дверью
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 2, "hse_blue")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 5, "paper")
    for wx in (x0 + 8, x0 + 36):
        rect(ld, wx, y0 + 12, wx + 14, y0 + 22, "glass")
        rect(ld, wx + 7, y0 + 12, wx + 7, y0 + 22, "paper")
    rect(ld, x0 + 56, y0 + 10, x0 + 68, y1 - 4, "base_dark")
    rect(ld, x0 + 1, y1 - 4, x1 - 1, y1 - 3, "hse_blue_dark")
    x0, y0, x1, y1 = cell(24, 8, 3, 2)  # поддоны с кирпичом
    for bx in (x0 + 1, x0 + 23):
        rect(ld, bx, y0 + 12, bx + 20, y1 - 2, "wood_dark")
        rect(ld, bx, y0 + 2, bx + 20, y0 + 20, "enemy_red_dark")
        for k in range(y0 + 5, y0 + 20, 5):
            rect(ld, bx, k, bx + 20, k, "enemy_red")
    x0, y0, x1, y1 = cell(27, 13, 3, 3)  # куча песка
    disc(ld, (x0 + x1) // 2, (y0 + y1) // 2 + 2, 20, "sand_dark")
    disc(ld, (x0 + x1) // 2 - 2, (y0 + y1) // 2, 16, "sand")
    for sx, sy in ((x0 + 10, y0 + 18), (x0 + 28, y0 + 10), (x0 + 22, y0 + 28)):
        rect(ld, sx, sy, sx + 2, sy, "sand_dark")
    for cx, cw in ((8, 3), (21, 3)):  # красно-белые барьеры
        x0, y0, x1, y1 = cell(cx, 7, cw, 1)
        rect(ld, x0 + 1, y0 + 4, x1 - 1, y0 + 10, "paper")
        for x in range(x0 + 1, x1 - 6, 10):
            rect(ld, x, y0 + 4, x + 4, y0 + 10, "exam_red")
        rect(ld, x0 + 3, y0 + 10, x0 + 5, y1 - 1, "base_dark")
        rect(ld, x1 - 5, y0 + 10, x1 - 3, y1 - 1, "base_dark")
    x0, y0, x1, y1 = cell(2, 14, 4, 1)  # трубы
    for k in range(3):
        rect(ld, x0 + 1, y0 + 2 + k * 4, x1 - 1, y0 + 5 + k * 4, "wall")
        rect(ld, x0 + 1, y0 + 2 + k * 4, x1 - 1, y0 + 2 + k * 4, "wall_light")
    for cx, cy in ((12, 9), (19, 9), (12, 12), (19, 12)):  # конусы (проходимые)
        x0, y0, x1, y1 = cell(cx, cy)
        rect(ld, x0 + 4, y0 + 10, x0 + 10, y0 + 12, "base_dark")
        rect(ld, x0 + 5, y0 + 4, x0 + 9, y0 + 9, "enemy_orange")
        rect(ld, x0 + 5, y0 + 6, x0 + 9, y0 + 7, "paper")
    lay_on(img, lay)
    arrow(img, 16 * HT, 82)
    doorway(d, img, 15, HH - HT, "door_in", "base_dark")
    return finish(img)


# ---------- двор Родионова
E2_WALLS = [[0, 0, 32, 5], [0, 5, 15, 1], [17, 5, 15, 1], [3, 9, 5, 2], [24, 9, 5, 2], [8, 13, 2, 1], [22, 13, 2, 1],
            [11, 8, 1, 1], [20, 8, 1, 1], [1, 13, 2, 2], [29, 13, 2, 2], [1, 6, 2, 2], [29, 6, 2, 2]]


def bike(ld, x, y):
    """Велосипед сверху: колёса-овалы и руль, цвета по номеру."""
    col = ("hse_blue", "exam_red", "bar_green", "pack")[(x // 7) % 4]
    rect(ld, x + 1, y, x + 3, y + 3, "outline")
    rect(ld, x, y + 2, x + 4, y + 2, "base_dark")
    rect(ld, x + 2, y + 3, x + 2, y + 13, col)
    rect(ld, x + 1, y + 11, x + 3, y + 14, "outline")


def bg_entrance_l2():
    """Родионова, мирная комната: двор у компьютерного корпуса. Светлый фасад со стеклянными поясами и
    синей полосой, стеклянные двери с жёлтым акцентом, на крыше антенны и блоки вентиляции,
    две велопарковки, скамейки, фонари, деревья. Вход снизу, выход — двери корпуса."""
    img = Image.new("RGBA", (HW, HH), P["asphalt"])
    d = ImageDraw.Draw(img)
    courtyard_ground(d, "asphalt", "asphalt_light", "asphalt_light")
    rect(d, 13 * HT, 90, 19 * HT - 1, HH - HT - 1, "path")
    dots(d, 120, 5, ["asphalt_light", "shadow_ground"])
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    hedge(ld, 0, 0, HT - 2, HH - 1)
    hedge(ld, HW - HT + 1, 0, HW - 1, HH - 1)
    hedge(ld, 0, HH - HT + 1, HW - 1, HH - 1)
    lay_on(img, lay)
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    building_top(ld, "step_b", "step_a", "hse_light", "hse_band", "paper")
    rect(ld, 0, 48, HW - 1, 55, "hse_blue")  # синий пояс
    rect(ld, 0, 56, HW - 1, 59, "paper")
    for x in range(8, HW - 8, 12):  # стеклянные ленты окон
        if 196 <= x <= 262:
            continue
        rect(ld, x, 40, x + 8, 46, "glass")
        rect(ld, x + 4, 40, x + 4, 46, "paper")
        rect(ld, x, 62, x + 8, 74, "glass")
        rect(ld, x + 4, 62, x + 4, 74, "paper")
        rect(ld, x, 68, x + 8, 68, "paper")
    for ax in (60, 400):  # блоки вентиляции и антенны на крыше
        rect(ld, ax, 8, ax + 18, 20, "hse_band")
        rect(ld, ax, 8, ax + 18, 9, "paper")
        rect(ld, ax + 3, 12, ax + 15, 17, "wall_dark")
    disc(ld, 130, 14, 7, "paper")
    disc(ld, 130, 14, 4, "step_b")
    rect(ld, 349, 6, 350, 28, "wall_light")
    rect(ld, 345, 6, 354, 7, "exam_red")
    rect(ld, 205, 60, 274, 66, "hse_blue")  # навес с жёлтой полосой
    rect(ld, 205, 66, 274, 66, "pack")
    rect(ld, 215, 67, 264, 88, "glass")
    for x in (215, 227, 239, 251, 263):
        rect(ld, x, 67, x + 1, 88, "paper")
    x0, y0, x1, y1 = cell(15, 5, 2, 1)
    rect(ld, x0, y0, x1, y1 - 1, "door_out")
    rect(ld, 215, 67, 264, 68, "pack")
    rect(ld, 210, 90, 269, 95, "step_a")
    rect(ld, 202, 96, 277, 101, "step_b")
    lay_on(img, lay)
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    for cx in (3, 24):  # велопарковки: рамка и четыре велосипеда
        x0, y0, x1, y1 = cell(cx, 9, 5, 2)
        rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 3, "base_dark")
        rect(ld, x0 + 1, y1 - 3, x1 - 1, y1 - 2, "base_dark")
        for k in range(5):
            bike(ld, x0 + 6 + k * 14, y0 + 8)
    for cx in (8, 22):  # скамейки
        x0, y0, x1, y1 = cell(cx, 13, 2, 1)
        rect(ld, x0 + 1, y0 + 4, x1 - 1, y0 + 9, "wood")
        rect(ld, x0 + 1, y0 + 4, x1 - 1, y0 + 5, "wood_light")
        rect(ld, x0 + 3, y0 + 10, x0 + 5, y0 + 13, "base_dark")
        rect(ld, x1 - 5, y0 + 10, x1 - 3, y0 + 13, "base_dark")
    for cx in (11, 20):  # фонари
        x0, y0, x1, y1 = cell(cx, 8)
        rect(ld, x0 + 6, y0 + 3, x0 + 8, y1 - 2, "base_dark")
        disc(ld, x0 + 7, y0 + 3, 4, "pack")
    for cx, cy in ((1, 13), (29, 13), (1, 6), (29, 6)):
        oak(ld, d, cx, cy)
    lay_on(img, lay)
    arrow(img, 16 * HT, 82)
    doorway(d, img, 15, HH - HT, "door_in", "leaf_dark")
    return finish(img)


# ---------- компьютерный класс Родионова
L2_DESKS = [(x, y) for x in (2, 7) for y in (5, 8, 11)] + [(x, y) for x in (21, 26) for y in (5, 8, 11)]
L2_WALLS = ([w for x, y in L2_DESKS for w in ([x, y, 4, 1], [x + 1, y + 1, 2, 1])]
            + [[14, 1, 4, 1], [1, 1, 3, 1], [5, 1, 3, 1], [30, 1, 1, 1]])


def bg_level2_class():
    """Родионова: самый технологичный класс. Ряды парт с двумя мониторами, серверные стойки, провода по полу,
    доска с кодом. Вход снизу, выход сверху (клетки 26-27)."""
    img, d = shell("dark_wall2", "dark_wall", lambda dd: tiles(dd, HT, HT, HW - HT, HH - HT, "tech_a", "tech_b", 15))
    for pts in (((130, 60), (130, 120), (160, 120), (160, 190), (180, 190)),
                ((330, 70), (330, 135), (300, 135), (300, 200)), ((60, 40), (60, 70), (110, 70), (110, 90))):
        cable(d, pts, "monitor")
    dots(d, 90, 7, ["paper", "step_b"])
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    chalkboard(ld, 160, 1, 380, [(8, 3, "x=5"), (36, 3, "if"), (56, 3, "for"), (84, 3, "print"), (126, 3, "def")])
    x0, y0, x1, y1 = cell(14, 1, 4, 1)
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 1, "tech_b")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 3, "paper")
    rect(ld, x0 + 1, y1 - 2, x1 - 1, y1 - 1, "base_dark")
    for mx in (x0 + 6, x0 + 34):
        rect(ld, mx, y0 + 3, mx + 17, y0 + 9, "monitor")
        rect(ld, mx + 1, y0 + 4, mx + 16, y0 + 7, "bar_green_light")
    for cx, sd in ((1, 0), (5, 2)):
        rack(ld, cx, 1, 3, 1, sd)
    for cx, cy in L2_DESKS:
        pc_desk(ld, cx, cy)
    x0, y0, x1, y1 = cell(30, 1)
    rect(ld, x0 + 3, y0 + 8, x1 - 3, y1 - 1, "pot")
    disc(ld, x0 + 7, y0 + 5, 6, "leaf_dark")
    disc(ld, x0 + 6, y0 + 4, 4, "leaf")
    lay_on(img, lay)
    put_door(img, d, 26, "base_dark")
    return finish(img)


# ---------- серверная Родионова (зал босса)
B2_WALLS = ([[x, y, 2, 2] for x in (1, 29) for y in (3, 6, 9, 12)]
            + [[4, 1, 4, 1], [9, 1, 4, 1], [19, 1, 4, 1], [24, 1, 4, 1]])


def bg_level2_boss():
    """Родионова, зал босса: серверная. Стойки с лампочками вдоль стен и у верхней стены, провода по полу к
    красному кольцу в центре, на мониторах ERROR. Центр свободен. Вход снизу, выход сверху (клетки 15-16)."""
    img, d = shell("dark_wall", "dark_wall2", lambda dd: tiles(dd, HT, HT, HW - HT, HH - HT, "dark_a", "dark_b", 15),
                   hi="purple")
    for r, col in ((82, "purple_dark"), (80, "exam_red"), (60, "purple_dark"), (58, "exam_red")):
        for a in range(0, 360, 2):
            d.point((int(240 + r * math.cos(math.radians(a))), int(135 + r * 0.82 * math.sin(math.radians(a)))), fill=P[col])
    for y in (135,):
        rect(d, 140, y, 340, y, "purple_dark")
    for pts, col in ((((30, 60), (60, 60), (60, 110), (150, 135)), "purple_light"),
                     (((450, 60), (420, 60), (420, 110), (330, 135)), "purple_light"),
                     (((30, 190), (70, 190), (70, 160), (150, 140)), "exam_red"),
                     (((450, 190), (410, 190), (410, 160), (330, 140)), "exam_red")):
        cable(d, pts, col)
    dots(d, 70, 11, ["purple_dark", "exam_red"])
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    for i, (cx, cy) in enumerate([(x, y) for x in (1, 29) for y in (3, 6, 9, 12)]):
        rack(ld, cx, cy, 2, 2, i)
    for i, cx in enumerate((4, 9, 19, 24)):
        rack(ld, cx, 1, 4, 1, i * 2, screen=(i % 2 == 0))
    lay_on(img, lay)
    put_door(img, d, 15, "purple_dark")
    return finish(img)


# ---------- зал босса Печерки: стройка
B1_WALLS = [[1, 3, 2, 4], [29, 3, 2, 4], [1, 10, 4, 2], [26, 12, 3, 2], [8, 1, 1, 1], [23, 1, 1, 1], [1, 14, 2, 2],
            [28, 15, 1, 1], [8, 15, 3, 1], [21, 15, 3, 1]]


def hazard_ring(d, x0, y0, x1, y1):
    for k in range(x0, x1, 8):
        rect(d, k, y0, k + 3, y0 + 1, "pack")
        rect(d, k, y1 - 1, k + 3, y1, "pack")
    for k in range(y0, y1, 8):
        rect(d, x0, k, x0 + 1, k + 3, "pack")
        rect(d, x1 - 1, k, x1, k + 3, "pack")


def bg_level1_boss():
    """Печерка, зал босса: строительный зал. Бетон, жёлто-чёрная разметка арены, леса вдоль стен,
    бетономешалка, рабочие лампы, на стене плакат EXAM и таймер. Центр свободен.
    Вход снизу, выход сверху (клетки 15-16)."""
    img, d = shell("wall_dark", "outline", lambda dd: tiles(dd, HT, HT, HW - HT, HH - HT, "concrete_a", "concrete_b", 15),
                   hi="enemy_orange")
    hazard_ring(d, 100, 55, 380, 215)
    dots(d, 170, 9, ["step_b", "sand_dark", "wall_dark"])
    for px, py in ((140, 120), (150, 126), (300, 150), (312, 144), (220, 190)):
        rect(d, px, py, px + 2, py + 1, "pack")
    for pts in (((120, 80), (135, 95), (132, 110), (150, 125)), ((350, 200), (335, 185), (340, 172), (322, 160)),
                ((250, 70), (258, 82), (252, 96))):  # трещины в бетоне
        d.line(pts, fill=P["wall_dark"], width=1)
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    rect(ld, 262, 1, 400, 13, "board_frame")  # табло экзамена правее двери
    rect(ld, 264, 2, 398, 11, "outline")
    text(ld, 272, 4, "EXAM", "exam_red")
    text(ld, 320, 4, "T-1", "exam_red")
    for cx in (8, 21):  # красно-белые барьеры у нижних углов арены
        x0, y0, x1, y1 = cell(cx, 15, 3, 1)
        rect(ld, x0 + 1, y0 + 4, x1 - 1, y0 + 10, "paper")
        for x in range(x0 + 1, x1 - 6, 10):
            rect(ld, x, y0 + 4, x + 4, y0 + 10, "exam_red")
        rect(ld, x0 + 3, y0 + 10, x0 + 5, y1 - 1, "base_dark")
        rect(ld, x1 - 5, y0 + 10, x1 - 3, y1 - 1, "base_dark")
    for cx, cy, h in ((1, 3, 4), (29, 3, 4)):  # леса вдоль боковых стен
        x0, y0, x1, y1 = cell(cx, cy, 2, h)
        for x in (x0 + 2, x1 - 3):
            rect(ld, x, y0, x + 1, y1, "enemy_orange_dark")
        for y in range(y0 + 2, y1, 14):
            rect(ld, x0 + 1, y, x1 - 1, y + 1, "wood")
            rect(ld, x0 + 1, y + 2, x1 - 1, y + 2, "wood_dark")
    x0, y0, x1, y1 = cell(1, 10, 4, 2)  # штабель мешков
    for bx, by in ((x0 + 1, y0 + 14), (x0 + 31, y0 + 14), (x0 + 16, y0 + 3), (x0 + 1, y0 + 3), (x0 + 31, y0 + 3)):
        rect(ld, bx, by, bx + 26, by + 12, "step_a")
        rect(ld, bx, by + 9, bx + 26, by + 12, "step_b")
        rect(ld, bx + 6, by + 4, bx + 20, by + 6, "enemy_red")
    x0, y0, x1, y1 = cell(26, 12, 3, 2)  # бетономешалка: барабан сверху
    disc(ld, x0 + 22, y0 + 15, 13, "base_dark")
    disc(ld, x0 + 22, y0 + 15, 10, "hse_blue")
    disc(ld, x0 + 22, y0 + 15, 4, "step_a")
    rect(ld, x0 + 2, y0 + 26, x0 + 10, y0 + 29, "wood_dark")
    for cx in (8, 23):  # рабочие лампы
        x0, y0, x1, y1 = cell(cx, 1)
        rect(ld, x0 + 6, y0 + 4, x0 + 8, y1 - 1, "base_dark")
        disc(ld, x0 + 7, y0 + 5, 5, "pack")
        disc(ld, x0 + 7, y0 + 5, 2, "paper")
    x0, y0, x1, y1 = cell(1, 14, 2, 2)  # стопка плит
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 2, "wood")
    for k in range(y0 + 6, y1 - 2, 6):
        rect(ld, x0 + 1, k, x1 - 1, k, "wood_dark")
    x0, y0, x1, y1 = cell(28, 15)  # знак «стоп» на красной стойке
    rect(ld, x0 + 6, y0 + 8, x0 + 8, y1 - 1, "base_dark")
    disc(ld, x0 + 7, y0 + 5, 5, "exam_red")
    rect(ld, x0 + 4, y0 + 5, x0 + 10, y0 + 5, "paper")
    lay_on(img, lay)
    put_door(img, d, 15, "enemy_orange_dark")
    return finish(img)


# ---------- зал экзамена Львовки (зал босса)
B3_WALLS = ([[x, y, 4, 1] for x in (2, 25) for y in (4, 7)] + [[x + 1, y + 1, 2, 1] for x in (2, 25) for y in (4, 7)]
            + [[x, y, 4, 1] for x in (2, 25) for y in (11, 14)] + [[x + 1, y + 1, 2, 1] for x in (2, 25) for y in (11, 14)]
            + [[6, 2, 16, 2], [1, 1, 2, 1], [30, 1, 1, 1]])


def bg_level3_boss():
    """Львовка, зал босса: экзаменационный зал. Длинный стол комиссии вверху (без людей: бланки, таймер,
    печать), красная дорожка к арене, ряды парт с бланками и красными отметками, табло. Центр свободен.
    Вход снизу (клетки 15-16), выход сверху (клетки 26-27)."""
    img, d = shell("wall_dark", "outline", lambda dd: floor_boards(dd, HT, HT, HW - HT, HH - HT, "lvov_floor_a", "lvov_floor_b"),
                   hi="hse_blue_dark")
    for r in (78, 74):  # красное кольцо арены (проходимое)
        for a in range(0, 360, 2):
            d.point((int(240 + r * math.cos(math.radians(a))), int(135 + r * 0.8 * math.sin(math.radians(a)))), fill=P["exam_red"])
    x0, y0, x1, y1 = cell(15, 13, 2, 4)  # красная дорожка
    rect(d, x0, y0, x1, y1, "exam_red")
    rect(d, x0 + 2, y0 + 2, x1 - 2, y1, "enemy_red_dark")
    rect(d, x0 + 4, y0 + 4, x1 - 4, y1, "exam_red")
    dots(d, 90, 13, ["shadow", "step_b"])
    for sx, sy in ((120, 110), (350, 100), (150, 185), (330, 175), (90, 150), (390, 150)):  # бланки на полу
        rect(d, sx, sy, sx + 7, sy + 9, "paper")
        rect(d, sx + 1, sy + 2, sx + 5, sy + 2, "step_b")
        rect(d, sx + 1, sy + 5, sx + 4, sy + 5, "step_b")
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    rect(ld, 160, 1, 380, 13, "board_frame")  # красное табло с формулами
    rect(ld, 162, 2, 378, 11, "outline")
    text(ld, 170, 4, "S", "exam_red")
    text(ld, 186, 4, "[a,b]", "exam_red")
    text(ld, 224, 4, "A^B", "exam_red")
    text(ld, 252, 4, "{xn}", "exam_red")
    text(ld, 296, 4, "F=2", "exam_red")
    x0, y0, x1, y1 = cell(6, 2, 16, 2)  # стол комиссии
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 1, "wood_dark")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 4, "wood")
    rect(ld, x0 + 1, y1 - 3, x1 - 1, y1 - 1, "brick_dark")
    for k in range(3):  # три рабочих места: бланки, табличка без имени, стопка
        px = x0 + 24 + k * 74
        rect(ld, px, y0 + 6, px + 30, y0 + 22, "paper")
        rect(ld, px + 3, y0 + 9, px + 27, y0 + 9, "step_b")
        rect(ld, px + 3, y0 + 13, px + 20, y0 + 13, "step_b")
        rect(ld, px + 8, y0 + 24, px + 22, y0 + 28, "pack")
        rect(ld, px + 36, y0 + 8, px + 44, y0 + 16, "step_a")
        rect(ld, px + 36, y0 + 8, px + 44, y0 + 9, "step_b")
    disc(ld, x0 + 118, y0 + 30, 6, "paper")  # таймер на столе
    disc(ld, x0 + 118, y0 + 30, 4, "exam_red")
    rect(ld, x0 + 118, y0 + 27, x0 + 118, y0 + 30, "paper")
    for i, (cx, cy) in enumerate(((2, 4), (2, 7), (25, 4), (25, 7), (2, 11), (2, 14), (25, 11), (25, 14))):
        desk(ld, cx, cy)
        bx, by, bx1, by1 = cell(cx, cy, 4, 1)
        exam_sheet(ld, bx + 8, by + 4, "2" if i % 3 == 0 else "F" if i % 3 == 1 else None)
    x0, y0, x1, y1 = cell(1, 1, 2, 1)
    rect(ld, x0 + 1, y0 + 1, x1 - 1, y1 - 1, "box")
    rect(ld, x0 + 1, y0 + 1, x1 - 1, y0 + 3, "wood_light")
    rect(ld, x0 + 13, y0 + 1, x0 + 16, y1 - 1, "wood_dark")
    x0, y0, x1, y1 = cell(30, 1)
    rect(ld, x0 + 3, y0 + 8, x1 - 3, y1 - 1, "pot")
    disc(ld, x0 + 7, y0 + 5, 6, "leaf_dark")
    disc(ld, x0 + 6, y0 + 4, 4, "leaf")
    lay_on(img, lay)
    put_door(img, d, 26, "hse_blue_dark")
    return finish(img)


# ---------------------------------------------------------------- враги, боссы и NPC набора
PALETTE.update({
    "hair_black": (40, 36, 52), "hair_blonde": (214, 170, 96),
})
P = PALETTE


# ---------- NPC: гуманоиды из тех же сеток, что и герой, свои цвета и предметы
ITEMS["none"] = dict(arm=["TTT", "TTT", "ttt", "SSS", "SSS"], far=None, near=(["T"], 12, 22))
ITEMS["flask"] = dict(arm=["TTT.L..", "TTT.L..", "ttt.LL.", "SSSLGGL", "...LGGL", "...LLLL"], far=None, near=(["T"], 12, 22))
CHARS["npc_l1_entrance_npc"] = dict(scale=1, dy=1, head="player", torso="player", item="none", gun="right", pack=False,
                                    pal={"H": "hse_blue_dark", "h": "hse_blue", "d": "outline", "T": "enemy_orange",
                                         "t": "enemy_orange_dark", "P": "pants_dark", "p": "outline", "O": "shoe",
                                         "Y": "pack", "y": "pack_dark", "F": "skin"})
CHARS["npc_l2_entrance_npc"] = dict(scale=1, dy=1, head="player", torso="player", item="flask", gun="right", pack=False,
                                    pal={"H": "hair", "h": "hair_light", "d": "hair_dark", "T": "paper", "t": "step_b",
                                         "P": "pants", "p": "pants_dark", "O": "shoe", "Y": "hse_blue", "y": "hse_blue_dark",
                                         "F": "skin", "G": "bar_green_light"})
CHARS["npc_l3_entrance_npc"] = dict(scale=1, dy=1, head="player", torso="player", item="book", gun="right", pack=False,
                                    pal={"H": "hair_black", "h": "wall_dark", "d": "outline", "T": "hse_blue",
                                         "t": "hse_blue_dark", "P": "pants", "p": "pants_dark", "O": "shoe",
                                         "Y": "hse_light", "y": "hse_band", "F": "skin"})
GLASSES_S = ["KKKK....KKKK", "KLEK.KK.KELK", "KLEK....KELK", "KKKK....KKKK"]  # светлое стекло, зрачок 1x2


def npc(name):
    img = character(name, "s", IDLE[0])
    return img


def npc_l1_entrance_npc():
    img = npc("npc_l1_entrance_npc")
    stamp(img, ["pppppp"], 13, 18, {"p": "hair_grey_dark"}, line=False)  # седые усы
    for k in range(12):  # метла: древко, соломенная щётка
        rect_px(img, 26, 12 + k, "wood_dark")
        rect_px(img, 27, 12 + k, "wood")
    stamp(img, ["yyyyyy", "yBByyB", "yyyyyy"], 23, 24, {"y": "pack_dark", "B": "wood_dark"})
    return img


def rect_px(img, x, y, col):
    img.putpixel((x, y), P[col] + (255,))


def npc_l2_entrance_npc():
    img = npc("npc_l2_entrance_npc")
    stamp(img, ["H..H..H.", "H.HH.HH.", "HHHHHHHH"], 12, 3, CHARS["npc_l2_entrance_npc"]["pal"])  # растрёпанные волосы
    stamp(img, GLASSES_S, 10, 15, {}, line=False)
    return img


def npc_l3_entrance_npc():
    img = npc("npc_l3_entrance_npc")
    stamp(img, GLASSES_S, 10, 15, {}, line=False)
    return img


# ---------------------------------------------------------------- враги и боссы с анимациями (8 направлений)
# Те же чиби-сетки, что у героя: голова 18x15, корпус 12x4, руки, ноги. Голову каждого существа получаем из
# голов героя (HEADS["player"]) инструментами ниже: перекраска, брови, очки, «кубическая» голова, клюв,
# надстройки сверху (плюмаж, пучок, антенна, гребень). Корпус рисуется своими сетками по 5 видам.
PALETTE.update({
    "enemy_red_light": (236, 104, 84), "enemy_orange_light": (255, 190, 110),
    "raven_grey": (170, 170, 176), "raven_grey_light": (206, 206, 212), "raven_grey_dark": (108, 108, 118),
    "beak_yellow": (246, 172, 28), "beak_dark": (206, 128, 10),
    "hair_plum": (66, 40, 78), "hair_plum_light": (104, 70, 120), "hair_plum_dark": (44, 26, 56),
})
P = PALETTE
COMMON.update({"w": "step_b", "G": "bar_green_light", "A": "led_amber", "D": "door_glass", "u": "brick_dark"})
VIEWS5 = ("s", "se", "e", "ne", "n")
FRONT3 = ("s", "se", "e")  # виды с лицом


def _set(g, pts):
    rows = [list(r) for r in g]
    for (x, y), ch in pts.items():
        if 0 <= y < len(rows) and 0 <= x < len(rows[y]):
            rows[y][x] = ch
    return ["".join(r) for r in rows]


def _eyes(g):
    """Глаза героя: K-пиксели на строках 10-11. Возвращает [(левый столбец, правый столбец)] слева направо."""
    cols = sorted({i for r in (10, 11) for i, ch in enumerate(g[r]) if ch == "K"})
    groups = []
    for c in cols:
        if groups and c - groups[-1][-1] <= 1:
            groups[-1].append(c)
        else:
            groups.append([c])
    return [(a[0], a[-1]) for a in groups]


def angry(g):
    """Злые брови: над каждым глазом чёрточка, внешний конец выше."""
    cl, pts = _eyes(g), {}
    for i, (c0, c1) in enumerate(cl):
        for x in range(c0, c1 + 1):
            pts[(x, 9)] = "K"
        if len(cl) == 2:
            pts[(c0 - 1, 8) if i == 0 else (c1 + 1, 8)] = "K"
        else:
            pts[(c0 - 1, 9)] = "K"
    return _set(g, pts)


def white_eyes(g):
    """Белок слева у левого глаза и справа у правого (зрачки смотрят к носу)."""
    cl, pts = _eyes(g), {}
    if len(cl) == 2:
        for y in (10, 11):
            pts[(cl[0][0], y)] = "W"
            pts[(cl[1][1], y)] = "W"
    return _set(g, pts)


def glasses(g):
    """Очки: рамка K вокруг глаз, светлое стекло L, перемычка и дужка."""
    cl, pts = _eyes(g), {}
    for i, (c0, c1) in enumerate(cl):
        for x in range(c0 - 1, c1 + 2):
            for y in (9, 12):
                if g[y][x] != "M":
                    pts[(x, y)] = "K"
        for y in (10, 11):
            pts[(c0 - 1, y)] = "K"
            pts[(c1 + 1, y)] = "K"
            if len(cl) == 2:
                pts[(c0 if i == 0 else c1, y)] = "L"
    if len(cl) == 2:
        for x in range(cl[0][1] + 2, cl[1][0] - 1):
            pts[(x, 10)] = "K"
    else:
        for x in range(cl[0][0] - 5, cl[0][0] - 1):
            pts[(x, 10)] = "K"
    return _set(g, pts)


def boxify(g):
    """Квадратная голова: закругления заполняются."""
    lo = min(next(i for i, ch in enumerate(r) if ch != ".") for r in g[5:11])
    hi = max(len(r.rstrip(".")) - 1 for r in g[5:11])
    fill = {0: "H", 1: "H", 2: "H", 3: "H", 4: "H", 11: "d", 12: "d", 13: "S", 14: "s"}
    rows = []
    for j, r in enumerate(g):
        rr = list(r)
        if j in fill:
            for x in range(lo, hi + 1):
                if rr[x] == ".":
                    rr[x] = fill[j]
        rows.append("".join(rr))
    return rows


def flat_mouth(g):
    """Без улыбки: прямая линия рта."""
    rows = [list(r) for r in g]
    rows[12] = [("S" if ch == "M" else ch) for ch in rows[12]]
    rows[13] = [("K" if ch == "M" else ch) for ch in rows[13]]
    return ["".join(r) for r in rows]


def prepend(g, rows, x_off):
    """Надстройка над головой: строки rows ставятся сверху со смещением x_off (голова сдвигается вниз при рисовании)."""
    w = len(g[0])
    return [("." * x_off + r).ljust(w, ".")[:w] for r in rows] + g


def recolor_row(g, y, a, b):
    rows = list(g)
    rows[y] = rows[y].replace(a, b)
    return rows


def _heads(fn):
    return {v: fn(v, HEADS["player"][v]) for v in VIEWS5}


# ---- Грамматический страж: красный шлем с оранжевой лентой и пером, злые брови, перо в руке
def _guard_head(v, g):
    if v in FRONT3:
        g = angry(g)
    g = recolor_row(g, 7, "H", "h")
    return prepend(g, ["...qf", "..qff", ".qffq"], {"s": 7, "se": 8, "e": 5, "ne": 8, "n": 7}[v])


# ---- Нулевик: красная кубическая голова с оранжевым лицом, оранжевое тело с цифрами 0 1 0
def _bin_head(v, g):
    g = flat_mouth(boxify(g))
    if v in FRONT3:
        g = white_eyes(angry(g))
    return g


_d0, _d1 = ["WWW", "W.W", "WWW"], ["WW.", ".W.", "WWW"]


def _digits(order, shift=0):
    rows = []
    for j in range(3):
        r = "T" + "T".join((_d0 if ch == "0" else _d1)[j].replace(".", "T") for ch in order)
        rows.append((r + "TT")[shift:shift + 12])
    return rows + ["t" * 12]


# ---- Интегралыч: оранжевая голова с красным завитком, тело — белый лист со знаком интеграла
def _int_head(v, g):
    if v in FRONT3:
        g = white_eyes(angry(g))
    return prepend(g, ["..rr.", ".r..r", ".r..."], {"s": 7, "se": 8, "e": 5, "ne": 8, "n": 7}[v])


# ---- Ворон ВШЭ (маскот): серый, светлый и тёмный бок, огромный жёлто-оранжевый клюв, круглые глаза, чёрный хохолок
def _bird_head(v, g, open_=False):
    g = [r.ljust(21, ".").replace("S", "H").replace("s", "d") for r in g]  # лицо того же серого, что голова
    g = [("".join("d" if (ch in "Hh" and i >= 13) else ch for i, ch in enumerate(r[:18])) + r[18:]) if v != "e"
         else ("".join("d" if (ch in "Hh" and i <= 2) else ch for i, ch in enumerate(r[:16])) + r[16:]) for r in g]  # тёмный бок
    pts = {}
    if v in ("s", "se"):
        cl = _eyes(g)
        for c0, c1 in cl:  # глаза героя стираем: у ворона они выше, под хохолком
            for x in range(c0, c1 + 1):
                for y in (10, 11):
                    pts[(x, y)] = "H"
        for i, (c0, c1) in enumerate(cl):  # круглые белые глаза 4x4 близко друг к другу, между ними просвет
            x0 = (4 if v == "s" else 7) if i == 0 else (10 if v == "s" else 12)
            for x in range(x0, x0 + 4):
                for y in (5, 6, 7, 8):
                    pts[(x, y)] = "W"
                pts[(x, 4)] = "K"
            for cx, cy in ((x0, 5), (x0 + 3, 5), (x0, 8), (x0 + 3, 8)):  # скруглённые углы
                pts[(cx, cy)] = "H"
            for y in (7, 8):  # зрачок 2x2 ближе к клюву
                for x in ((x0 + 2, x0 + 3) if i == 0 else (x0, x0 + 1)):
                    pts[(x, y)] = "K"
            pts[(x0 - 1 if i == 0 else x0 + 4, 3)] = "K"
        dx = 0 if v == "s" else 3
        rows = ((9, 4, 14, "B"), (10, 5, 13, "B"), (11, 6, 12, "B"), (12, 7, 11, "b"), (13, 8, 10, "b"))  # клюв-треугольник
        if open_:  # клюв открыт: верхняя часть выше, нижняя ниже, между ними тёмный зев
            rows = ((9, 4, 14, "B"), (10, 5, 13, "B"), (11, 6, 12, "K"), (12, 6, 12, "b"), (13, 7, 11, "b"), (14, 8, 10, "b"))
        for y, x0, x1, ch in rows:
            for x in range(x0 + dx, x1 + dx):
                pts[(x, y)] = ch
    elif v == "e":
        for y in (10, 11):
            pts[(13, y)] = "H"
        for x in range(9, 13):
            for y in (5, 6, 7, 8):
                pts[(x, y)] = "W"
        for cx, cy in ((9, 5), (12, 5), (9, 8)):
            pts[(cx, cy)] = "H"
        for y in (7, 8):
            pts[(11, y)] = "K"
            pts[(12, y)] = "K"
        for x in range(9, 13):
            pts[(x, 4)] = "K"
        pts[(8, 3)] = "K"
        beak_e = ((8, 13, 16, "B"), (9, 13, 18, "B"), (10, 13, 21, "B"), (11, 13, 20, "b"), (12, 13, 17, "b"))
        if open_:
            beak_e = ((7, 13, 16, "B"), (8, 13, 21, "B"), (9, 13, 20, "K"), (10, 13, 19, "K"), (11, 13, 18, "b"), (12, 13, 20, "b"), (13, 14, 17, "b"))
        for y, x0, x1, ch in beak_e:
            for x in range(x0, x1):
                pts[(x, y)] = ch
    elif v == "ne":
        beak_ne = ((9, 17, 20, "B"), (10, 17, 20, "B"), (11, 17, 19, "b"))
        if open_:
            beak_ne = ((8, 17, 20, "B"), (9, 17, 20, "K"), (10, 17, 19, "b"), (11, 17, 19, "b"))
        for y, x0, x1, ch in beak_ne:
            for x in range(x0, x1):
                pts[(x, y)] = ch
    g = _set(g, pts)
    return prepend(g, ["..K....", ".KK.K..", ".KK.KK.", "KKKKKKK"], {"s": 6, "se": 7, "e": 4, "ne": 7, "n": 6}[v])  # хохолок из чёрных перьев


# ---- Хозяин сервера: фиолетовый «монитор» с тёмным экраном, красные глаза и рот, лампочки, антенна
def _srv_head(v, g):
    g = boxify(g)
    if v in FRONT3:
        g = angry(flat_mouth(g))
    else:
        g = _set(g, {(x, y): "d" for y in (8, 10) for x in range(4, 14) if g[y][x] != "."})
    rows = [list(r) for r in g]
    for k, x in enumerate(range(3, len(rows[0]) - 3, 3)):
        if rows[6][x] != ".":
            rows[6][x] = "G" if k % 2 == 0 else "A"
    g = ["".join(r).replace("S", "D").replace("s", "u") for r in rows]  # лицо — тёмный экран; S остаётся рукам (штекеры)
    return prepend(g, ["RR", "pp", "pp"], {"s": 8, "se": 9, "e": 6, "ne": 9, "n": 8}[v])


# ---- Учительница английского: сливовые волосы с пучком, очки, фиолетовый кардиган, красный шарф
def _teacher_head(v, g):
    if v in FRONT3:
        g = glasses(angry(g))
    return prepend(g, ["..HHH.", ".HHhHH", ".HHHH."], {"s": 6, "se": 7, "e": 2, "ne": 7, "n": 6}[v])


HEADS.update({
    "guard": _heads(_guard_head), "bin": _heads(_bin_head), "integral": _heads(_int_head),
    "bird": _heads(_bird_head), "bird_open": _heads(lambda v, g: _bird_head(v, g, True)), "server": _heads(_srv_head), "teacher": _heads(_teacher_head),
})
TORSOS.update({
    "bin": {"s": _digits("010"), "se": _digits("010", 1), "ne": _digits("101", 1), "n": _digits("101"),
            "e": ["TTWWWTTT", "TTW.WTTT", "TTWWWTTT", "tttttttt"]},
    "integral": {
        "s": ["WWWWWWRRWWWW", "WWWWWWRWWWWW", "WWWWWRRWWWWW", "wwwwwwwwwwww"],
        "se": ["WWWWWWWRRWWW", "WWWWWWWRWWWW", "WWWWWWRRWWWW", "wwwwwwwwwwww"],
        "e": ["WWWWWRRW", "WWWWWRWW", "WWWWRRWW", "wwwwwwww"],
        "ne": ["WwwwwwwwwWWW", "WWWWWWWWWWWW", "WwwwwwwWWWWW", "wwwwwwwwwwww"],
        "n": ["WwwwwwwwwwWW", "WWWWWWWWWWWW", "WwwwwwwwWWWW", "wwwwwwwwwwww"]},
    "bird": {
        "s": ["TTTTTTTTTttt", "TTTTTTTTTttt", "TTTTTTTTTttt", "tttttttttttt"],
        "se": ["TTTTTTTTTttt", "TTTTTTTTTttt", "TTTTTTTTTttt", "tttttttttttt"],
        "e": ["TTTTTTtt", "TTTTTTtt", "TTTTTTtt", "tttttttt"],
        "ne": ["TTTTTTTTTTtt", "TTTTTTTTTTtt", "TTTTTTTTTTtt", "tttttttttttt"],
        "n": ["TTTTTTTTTTtt", "TTTTTTTTTTtt", "TTTTTTTTTTtt", "tttttttttttt"]},
    "server": {
        "s": ["TuGuAuGuAuuT", "TuuuuuuuuuuT", "TuRuGuAuRuuT", "tttttttttttt"],
        "se": ["TTuGuAuGuAuT", "TTuuuuuuuuuT", "TTuRuGuAuRuT", "tttttttttttt"],
        "e": ["TuGuAuuT", "TuuuuuuT", "TuAuRuuT", "tttttttt"],
        "ne": ["TuuuuuuuuuuT", "TtuuuuuuuutT", "TuuuuuuuuuuT", "tttttttttttt"],
        "n": ["TuuuuuuuuuuT", "TtuuuuuuuutT", "TuuuuuuuuuuT", "tttttttttttt"]},
})
ITEMS["quill"] = dict(  # перо в левой руке: рукоять B, опахало f/q
    arm=["TTT..qf", "TTT.qff", "tttqff.", "SSSBf..", "SSS.B..", "....B.."],
    far=([".qf", "qff", "Bf.", "B..", "B.."], 19, 19),
    near=(["fq.", "ffq", ".fB", "..B", "..B"], 11, 19))
THIN_LEGS = ([".P.", ".P.", ".P.", "OOO"], [".P.", ".P.", ".P.", "OOO"], [".P.", ".P.", ".P.", "OOO"])  # одна чёрная линия и лапка
CHARS.update({
    "enemy_english_melee": dict(scale=1, dy=1, head="guard", torso="player", item="quill", gun="left", pack=False,
                                melee=True, slash=12,
                                pal={"H": "enemy_red", "h": "enemy_orange", "d": "enemy_red_dark", "T": "enemy_red",
                                     "t": "enemy_red_dark", "Y": "enemy_orange", "y": "enemy_orange_dark",
                                     "P": "wood_dark", "p": "outline", "O": "wall_dark", "F": "enemy_orange",
                                     "q": "enemy_orange", "f": "paper", "B": "wood_dark"}),
    "enemy_binary_melee": dict(scale=1, dy=1, head="bin", torso="bin", item="none", gun="right", pack=False,
                               melee=True, slash=12,
                               pal={"H": "enemy_red", "h": "enemy_red_light", "d": "enemy_red_dark", "S": "enemy_orange",
                                    "s": "enemy_orange_dark", "T": "enemy_orange", "t": "enemy_orange_dark",
                                    "P": "enemy_red_dark", "p": "outline", "O": "wall_dark", "F": "paper"}),
    "enemy_formula_melee": dict(scale=1, dy=1, head="integral", torso="integral", item="none", gun="right",
                                pack=False, melee=True, slash=12,
                                pal={"H": "enemy_orange", "h": "enemy_orange_light", "d": "enemy_orange_dark",
                                     "S": "enemy_orange_light", "s": "enemy_orange", "T": "enemy_orange",
                                     "t": "enemy_orange_dark", "P": "enemy_orange_dark", "p": "outline",
                                     "O": "enemy_red_dark", "r": "enemy_red", "F": "paper"}),
    "enemy_hse_bird": dict(scale=1, dy=1, head="bird", head_open="bird_open", torso="bird", item="none", gun=None,
                           pack=False, legs=THIN_LEGS, legs_x=(12, 17), legs_line=False,
                           pal={"H": "raven_grey", "h": "raven_grey_light", "d": "raven_grey_dark",
                                "T": "raven_grey", "t": "raven_grey_dark", "S": "raven_grey_dark",
                                "P": "outline", "p": "outline", "O": "outline", "B": "beak_yellow", "b": "beak_dark"}),
    "boss_level1": dict(scale=2, dy=1, head="teacher", torso="player", item="book", gun="right", pack=False,
                        pal={"H": "hair_plum", "h": "hair_plum_light", "d": "hair_plum_dark", "M": "exam_red",
                             "T": "purple", "t": "purple_dark", "Y": "exam_red", "y": "enemy_red_dark",
                             "P": "purple_dark", "p": "dark_wall", "O": "exam_red", "F": "paper"}),
    "boss_level2": dict(scale=2, dy=1, head="server", torso="server", item="none", gun="right", pack=False,
                        pal={"H": "purple", "h": "purple_light", "d": "purple_dark", "S": "pack", "s": "pack_dark",
                             "K": "hit_red", "M": "hit_red", "R": "hit_red", "p": "purple_dark", "T": "purple_dark",
                             "t": "dark_wall", "P": "purple_dark", "O": "brick_dark", "F": "led_amber"}),
})


def save_bird(name):
    """Стреляющий клювом (ворон ВШЭ): покой 2, ходьба 4, выстрел 2 (1 — клюв открыт, 2 — закрыт) на 8 направлений."""
    for dr in DIRS:
        for k, ph in enumerate(IDLE, 1):
            save(character(name, dr, ph), "%s_idle_%s_%d" % (name, dr, k))
        for k, ph in enumerate(WALK, 1):
            save(character(name, dr, ph), "%s_walk_%s_%d" % (name, dr, k))
        save(character(name, dr, STAND, beak=True), "%s_shoot_%s_1" % (name, dr))
        save(character(name, dr, STAND), "%s_shoot_%s_2" % (name, dr))
    save(character(name, "s", IDLE[0]), name)  # запасной кадр: смотрит вниз


def save_creature(name):
    """Враг ближнего боя: покой 2, ходьба 4, удар стоя 2 (замах, удар), удар на ходу 4 кадра на 8 направлений."""
    for dr in DIRS:
        for k, ph in enumerate(IDLE, 1):
            save(character(name, dr, ph), "%s_idle_%s_%d" % (name, dr, k))
        for k, ph in enumerate(WALK, 1):
            save(character(name, dr, ph), "%s_walk_%s_%d" % (name, dr, k))
            walkatk = "windup" if k in (1, 4) else "strike"
            leg = ATK_WINDUP if walkatk == "windup" else ATK_STRIKE
            save(character(name, dr, (ph[0], ph[1], leg[2], leg[3], leg[4]), atk=walkatk),
                 "%s_walkattack_%s_%d" % (name, dr, k))
        save(character(name, dr, ATK_WINDUP, atk="windup"), "%s_attack_%s_1" % (name, dr))
        save(character(name, dr, ATK_STRIKE, atk="strike"), "%s_attack_%s_2" % (name, dr))
    save(character(name, "s", IDLE[0]), name)  # запасной кадр: смотрит вниз


# ---------------------------------------------------------------- лечилка: стакан кофе с крышкой
def _heal_grid():
    """Бумажный стакан кофе на вынос: тёмная крышка с отверстием, суживающийся белый корпус,
    коричневый ободок с кофейным зерном. Вид в три четверти, ширина 16, строка = один пиксель."""
    rows = []
    def add(width, fill, edge_l="", edge_r=""):
        body = fill * (width - len(edge_l) - len(edge_r))
        rows.append((edge_l + body + edge_r).center(16, "."))
    add(8, "L")                                   # крышка: верхний овал
    rows.append("LLLLLLLLLLLL".center(16, "."))
    rows.append("LLLLLLLLKDDLLL"[:14].center(16, "."))  # отверстие для питья
    rows.append("lllllllllllllll".ljust(16, "l")[:16])  # край крышки
    rows.append("LLLLLLLLLLLLLL".center(16, "."))      # тень под краем
    for i in range(14):                           # корпус: от 14 до 10 пикселей
        w = 14 - (i * 4) // 13
        if 3 <= i <= 8:                           # коричневый ободок
            rows.append(("o" + "S" * (w - 3) + "qq").center(16, "."))
        else:
            rows.append(("W" + "W" * (w - 3) + "ss").center(16, "."))
    # зерно на ободке: два овала со светлой чёрточкой
    bean = [(7, 9), (8, 9), (6, 10), (7, 10), (8, 10), (9, 10), (6, 11), (7, 11), (8, 11), (9, 11), (7, 12), (8, 12)]
    grid = [list(r) for r in rows]
    for x, y in bean:
        grid[y][x + 1] = "q"
    for x, y in ((8, 10), (8, 11)):
        grid[y][x + 1] = "o"
    return ["".join(r) for r in grid]


HEAL_PAL = {"L": "wall_dark", "l": "wall_light", "D": "door_glass", "W": "paper", "s": "step_b", "S": "wood",
            "q": "wood_dark", "o": "wood_light"}


def fx_heal():
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    stamp(img, SHADOW, 9, 28, {}, line=False)
    stamp(img, _heal_grid(), 8, 9, HEAL_PAL)
    for x, y in ((14, 7), (15, 6), (14, 5), (15, 4), (16, 3), (19, 6), (20, 5), (19, 4), (20, 3)):  # пар над крышкой
        img.putpixel((x, y), P["paper"] + (255,))
    return img


HEAL_STEAM = ((14, 7), (15, 6), (14, 5), (15, 4), (16, 3), (19, 6), (20, 5), (19, 4), (20, 3))


def _cup_3d(rot):
    """Объёмный стакан: конус с поверхностью, повёрнутой на rot рад. Свет слева, тень справа,
    логотип-зерно и шов на рукаве реально уезжают за край, крышка с отверстием вращается вместе с ним."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    px = img.load()
    cx = 16
    def wrap(a):
        return (a + math.pi) % (2 * math.pi) - math.pi
    def side(y, r, light, mid, dark, tex=None):
        for x in range(cx - r, cx + r):
            t = (x + 0.5 - cx) / r  # -1 слева .. 1 справа
            phi = math.asin(max(-1, min(1, t))) + rot
            col = light if t < -0.45 else dark if t > 0.5 else mid
            if tex:
                col = tex(x, y, t, phi, col)
            px[x, y] = col + (255,)
    lid, lid_l, lid_d = P["wall_dark"], P["wall_light"], P["outline"]
    # верх крышки: овал с отверстием, которое ходит по кругу
    for y in range(9, 14):
        for x in range(cx - 7, cx + 7):
            ex, ey = (x + 0.5 - cx) / 7, (y - 11) / 2.4
            if ex * ex + ey * ey <= 1:
                px[x, y] = lid_l + (255,) if ey < 0.2 else lid + (255,)
    hx, hy = cx + round(3.5 * math.cos(rot + 0.6)), 11 + round(1.1 * math.sin(rot + 0.6))
    for dx in (-1, 0):
        if 0 <= hx + dx < 32:
            px[hx + dx, hy] = lid_d + (255,)
    for y, r in ((13, 8), (14, 8)):  # борт крышки
        side(y, r, lid_l, lid, lid_d)
    side(15, 7, lid, lid, lid_d)
    wh, sh = P["paper"], P["step_b"]
    def sleeve(x, y, t, phi, col):
        if not 18 <= y <= 23:
            return col
        base = (P["wood_light"], P["wood"], P["wood_dark"])[0 if t < -0.45 else 2 if t > 0.5 else 1]
        d = abs(wrap(phi))
        if t > -1 and math.cos(phi) > 0.05 and d < 0.42 and 19 <= y <= 22:  # зерно-логотип
            if (y in (20, 21)) and d < 0.1:
                return P["wood_light"]
            return P["wood_dark"]
        if abs(wrap(phi - math.pi)) < 0.14:  # шов
            return P["wood_dark"]
        return base
    for y in range(16, 28):
        r = 7 - ((y - 16) * 2) // 11
        if y == 27:
            r -= 1
        side(y, r, wh, wh, sh, tex=sleeve)
    return img


def fx_heal_float(frame):
    """Кадр 1..8 парящего стакана: покачивание вверх-вниз (0..2 px) и вращение вокруг вертикальной оси
    (настоящее, с поворотом поверхности и светом). Цикл 8 кадров, тень остаётся на земле."""
    i = frame - 1
    bob = -round(1 + math.sin(2 * math.pi * i / 8))
    cup = _cup_3d(2 * math.pi * i / 8)
    outline(cup, P["outline"])
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    stamp(img, SHADOW, 9, 28, {}, line=False)
    img.alpha_composite(cup, (0, bob))
    for x, y in HEAL_STEAM:  # пар колышется
        img.putpixel((x + (i % 2 if y % 2 else 0), y + bob), P["paper"] + (255,))
    return img


PLAYER_DIRS = ("s", "se", "e", "ne", "n", "nw", "w", "sw")


def brown_tint(src):
    """Коричневая заливка кадра (контур остаётся тёмным), для мигания при подборе кофе."""
    src = src.convert("RGBA")
    px = src.load()
    ramp = (P["wood_dark"], P["wood"], P["wood_light"])
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = px[x, y]
            if a != 255 or (r, g, b) == P["outline"]:
                continue
            lum = 0.3 * r + 0.59 * g + 0.11 * b
            px[x, y] = ramp[0 if lum < 90 else 1 if lum < 160 else 2] + (255,)
    return src


def player_heal(d, frame):
    """Подбор кофе стоя: кадры 1 и 3 коричневые, 2 и 4 обычные."""
    src = Image.open(os.path.join(OUT, "player_idle_%s_1.png" % d))
    return src.convert("RGBA") if frame % 2 == 0 else brown_tint(src)


PLAYER_ANIMS = (("idle", 2), ("walk", 4), ("shoot", 2), ("walkshoot", 4))


def save_heal_anim():
    for f in range(1, 9):
        save(fx_heal_float(f), "fx_heal_float_%d" % f)
    for d in PLAYER_DIRS:
        for f in range(1, 5):
            save(player_heal(d, f), "player_heal_%s_%d" % (d, f))
    for anim, n in PLAYER_ANIMS:  # коричневая копия каждого кадра героя: для мигания при подборе в любом действии
        for d in PLAYER_DIRS:
            for f in range(1, n + 1):
                src = Image.open(os.path.join(OUT, "player_%s_%s_%d.png" % (anim, d, f)))
                save(brown_tint(src), "player_brown_%s_%s_%d" % (anim, d, f))


# ---------------------------------------------------------------- четвёртые комнаты уровней (тревожнее обычных)
# Порядок на уровне: двор -> комната уровня -> эта комната (больше деталей, ближе экзамен) -> зал босса.
def _plywood(ld, cx, cy, cw, ch):
    """Фанерная перегородка из листов со швами и красной лентой."""
    x0, y0, x1, y1 = cell(cx, cy, cw, ch)
    rect(ld, x0 + 3, y0 + 1, x1 - 3, y1 - 1, "wood_light")
    for y in range(y0 + 8, y1 - 2, 12):
        rect(ld, x0 + 3, y, x1 - 3, y, "wood")
    rect(ld, x0 + 3, y0 + 1, x0 + 4, y1 - 1, "wood")
    rect(ld, x0 + 3, (y0 + y1) // 2, x1 - 3, (y0 + y1) // 2 + 1, "exam_red")


def _scaffold(ld, cx, cy, cw, ch):
    x0, y0, x1, y1 = cell(cx, cy, cw, ch)
    for x in (x0 + 2, x1 - 3):
        rect(ld, x, y0, x + 1, y1, "enemy_orange_dark")
    for y in range(y0 + 2, y1, 14):
        rect(ld, x0 + 1, y, x1 - 1, y + 1, "wood")
        rect(ld, x0 + 1, y + 2, x1 - 1, y + 2, "wood_dark")


def _mixer(ld, cx, cy, cw, ch):
    x0, y0, x1, y1 = cell(cx, cy, cw, ch)
    mx, my = x0 + 22, y0 + 15
    disc(ld, mx, my, 13, "base_dark")
    disc(ld, mx, my, 10, "hse_blue")
    disc(ld, mx, my, 4, "step_a")
    rect(ld, x0 + 2, y0 + 26, x0 + 10, y0 + 29, "wood_dark")


def _barrier(ld, cx, cy, cw):
    x0, y0, x1, y1 = cell(cx, cy, cw, 1)
    rect(ld, x0 + 1, y0 + 4, x1 - 1, y0 + 10, "paper")
    for x in range(x0 + 1, x1 - 6, 10):
        rect(ld, x, y0 + 4, x + 4, y0 + 10, "exam_red")
    rect(ld, x0 + 3, y0 + 10, x0 + 5, y1 - 1, "base_dark")
    rect(ld, x1 - 5, y0 + 10, x1 - 3, y1 - 1, "base_dark")


Y2_WALLS = [[6, 5, 1, 5], [25, 8, 1, 5], [1, 3, 2, 3], [29, 3, 2, 3], [11, 12, 3, 2], [18, 11, 4, 2], [3, 13, 2, 1],
            [1, 9, 3, 2], [20, 5, 3, 1], [9, 4, 3, 1], [14, 1, 4, 1]]


def bg_level1_yard2():
    """Печерка, вторая комната: ремонт в разгаре. Фанерные перегородки, леса, бетономешалка, поддоны с досками,
    краска, парты под плёнкой, красно-белые барьеры, доска закрыта плёнкой, красная лента на полу.
    Вход снизу (клетки 15-16), выход сверху (клетки 26-27)."""
    img, d = shell("wall_dark", "outline", lambda dd: tiles(dd, HT, HT, HW - HT, HH - HT, "concrete_a", "concrete_b", 15),
                   hi="enemy_orange")
    repair_walls(d)
    for x0, y0, x1, y1 in ((60, 0, 130, 13), (300, 0, 380, 13)):  # проломы в верхней стене
        rect(d, x0, y0, x1, y1, "brick_dark")
        for k in range(x0 + 3, x1, 9):
            d.point((k, y0 + 5), fill=P["outline"])
    dots(d, 220, 13, ["step_b", "sand_dark", "wall_dark"])
    for y in range(60, 200, 8):  # красная лента через комнату (проходимая)
        rect(d, 200, y, 203, y + 3, "exam_red" if (y // 8) % 2 else "paper")
    for pts in (((50, 70), (70, 90), (66, 110)), ((420, 150), (400, 172), (408, 196)), ((250, 200), (262, 214), (256, 232))):
        d.line(pts, fill=P["wall_dark"], width=1)  # трещины в бетоне
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    chalkboard(ld, 160, 1, 380, [(8, 3, "Hello"), (50, 3, "a/an"), (88, 3, "I am"), (130, 3, "-ed")])
    rect(ld, 270, 2, 378, 12, "screen")  # плёнка поверх половины доски
    for x in range(278, 378, 14):
        rect(ld, x, 2, x + 1, 12, "glass")
    x0, y0, x1, y1 = cell(14, 1, 4, 1)  # стол под доской: каска, бумаги, красная папка
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 1, "wood")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 3, "wood_light")
    rect(ld, x0 + 1, y1 - 2, x1 - 1, y1 - 1, "wood_dark")
    disc(ld, x0 + 14, y0 + 8, 4, "pack")
    rect(ld, x0 + 10, y0 + 8, x0 + 18, y0 + 9, "pack_dark")
    rect(ld, x0 + 32, y0 + 5, x0 + 50, y0 + 11, "paper")
    rect(ld, x0 + 3, y0 + 5, x0 + 7, y0 + 11, "exam_red")
    _plywood(ld, 6, 5, 1, 5)
    _plywood(ld, 25, 8, 1, 5)
    _scaffold(ld, 1, 3, 2, 3)
    _scaffold(ld, 29, 3, 2, 3)
    _mixer(ld, 11, 12, 3, 2)
    x0, y0, x1, y1 = cell(18, 11, 4, 2)  # поддоны с досками
    for k, by in enumerate((y0 + 22, y0 + 12, y0 + 2)):
        rect(ld, x0 + 2, by, x1 - 2, by + 8, "wood" if k % 2 else "wood_light")
        rect(ld, x0 + 2, by + 7, x1 - 2, by + 8, "wood_dark")
    for cx in (3, 4):  # банки с краской
        x0, y0, x1, y1 = cell(cx, 13)
        disc(ld, (x0 + x1) // 2, (y0 + y1) // 2, 6, "step_b")
        disc(ld, (x0 + x1) // 2, (y0 + y1) // 2, 4, "enemy_orange" if cx == 3 else "exam_red")
    x0, y0, x1, y1 = cell(1, 9, 3, 2)  # парты под плёнкой
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 2, "screen")
    for k in range(7, x1 - x0 - 3, 13):
        rect(ld, x0 + k, y0 + 2, x0 + k + 1, y1 - 2, "glass")
    rect(ld, x0 + 4, y1 - 1, x0 + 6, y1, "wood_dark")
    rect(ld, x1 - 6, y1 - 1, x1 - 4, y1, "wood_dark")
    _barrier(ld, 20, 5, 3)
    _barrier(ld, 9, 4, 3)
    lay_on(img, lay)
    put_door(img, d, 26, "enemy_orange_dark")
    return finish(img)


# ---------- Родионова: сломавшийся компьютерный класс
L2B_DESKS = [(8, 6), (8, 10), (20, 6), (20, 10)]
L2B_WALLS = ([[1, 3, 2, 3], [1, 7, 2, 3], [1, 11, 2, 3], [29, 3, 2, 3], [14, 1, 4, 1]]
             + [w for x, y in L2B_DESKS for w in ([x, y, 4, 1], [x + 1, y + 1, 2, 1])])


def pc_desk_err(ld, cx, cy):
    """Компьютерная парта с экранами в красных ошибках."""
    x0, y0, x1, y1 = cell(cx, cy, 4, 1)
    rect(ld, x0 + 20, y1 + 2, x1 - 20, y1 + 10, "wall")
    rect(ld, x0 + 20, y1 + 9, x1 - 20, y1 + 10, "wall_dark")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 1, "tech_b")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 3, "paper")
    rect(ld, x0 + 1, y1 - 2, x1 - 1, y1 - 1, "base_dark")
    for k in range(2):
        mx = x0 + 6 + k * 26
        rect(ld, mx, y0 + 3, mx + 17, y0 + 9, "monitor")
        rect(ld, mx + 1, y0 + 4, mx + 16, y0 + 7, "exam_red")
        rect(ld, mx + 3, y0 + 5, mx + 12, y0 + 5, "paper")
        rect(ld, mx + 4, y0 + 10, mx + 13, y0 + 10, "paper")


def bg_level2_class2():
    """Родионова, вторая комната: сломавшийся класс. Стойки вдоль стен, парты с красными ошибками,
    провода по всему полу, красная полоса у выхода, экраны ERROR на стене.
    Вход снизу (клетки 15-16), выход сверху (клетки 26-27)."""
    img, d = shell("dark_wall2", "dark_wall", lambda dd: tiles(dd, HT, HT, HW - HT, HH - HT, "tech_b", "tech_a", 15))
    for pts, col in ((((60, 60), (60, 120), (130, 120), (130, 180), (200, 180)), "exam_red"),
                     (((60, 100), (100, 100), (100, 200), (160, 200)), "monitor"),
                     (((420, 60), (420, 130), (350, 130), (350, 200)), "led_amber"),
                     (((300, 70), (300, 120), (250, 120), (250, 170), (210, 170)), "purple_dark"),
                     (((60, 190), (90, 190), (90, 230), (180, 230)), "exam_red"),
                     (((440, 100), (390, 100), (390, 215)), "monitor")):
        cable(d, pts, col)
    for y in range(18, 34, 4):  # предупреждающая полоса перед выходом
        for x in range(390, 420, 8):
            rect(d, x, y, x + 3, y + 1, "pack")
    for px, py in ((140, 150), (310, 160), (260, 60), (380, 190)):  # осколки, бумага
        rect(d, px, py, px + 3, py + 2, "paper")
    dots(d, 120, 17, ["paper", "step_b", "exam_red"])
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    for x0 in (170, 255, 340):  # мониторы на стене, на каждом ERROR
        rect(ld, x0, 2, x0 + 40, 12, "monitor")
        rect(ld, x0 + 2, 3, x0 + 38, 11, "outline")
        text(ld, x0 + 11, 5, "ERROR", "hit_red")
    x0, y0, x1, y1 = cell(14, 1, 4, 1)
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 1, "tech_b")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 3, "paper")
    rect(ld, x0 + 1, y1 - 2, x1 - 1, y1 - 1, "base_dark")
    for mx in (x0 + 6, x0 + 34):
        rect(ld, mx, y0 + 3, mx + 17, y0 + 9, "monitor")
        rect(ld, mx + 1, y0 + 4, mx + 16, y0 + 7, "hit_red")
    for i, (cx, cy) in enumerate([(1, 3), (1, 7), (1, 11), (29, 3)]):
        rack(ld, cx, cy, 2, 3, i * 2, screen=False)
    for cx, cy in L2B_DESKS:
        pc_desk_err(ld, cx, cy)
    lay_on(img, lay)
    put_door(img, d, 26, "exam_red")
    return finish(img)


# ---------- Львовка: аудитория перед экзаменом
H2_DESKS = [(4, 4), (4, 7), (4, 10), (4, 13), (22, 4), (22, 7), (22, 10), (22, 13)]
H2_WALLS = ([w for x, y in H2_DESKS for w in ([x, y, 4, 1], [x + 1, y + 1, 2, 1])]
            + [[14, 1, 4, 1], [1, 1, 2, 1], [30, 1, 1, 1], [29, 14, 2, 2], [1, 16, 3, 1]])


def bg_level3_hall2():
    """Львовка, вторая комната: аудитория перед экзаменом. Парты рядами с бланками, на доске формулы и таймер,
    часы на стене, стопки бумаг, тёмные стены. Вход снизу (клетки 15-16), выход сверху (клетки 26-27)."""
    img, d = shell("wall_dark", "outline", lambda dd: floor_boards(dd, HT, HT, HW - HT, HH - HT), hi="hse_blue_dark")
    x0, y0, x1, y1 = cell(15, 13, 2, 4)  # красная дорожка
    rect(d, x0, y0, x1, y1, "exam_red")
    rect(d, x0 + 2, y0 + 2, x1 - 2, y1, "enemy_red_dark")
    rect(d, x0 + 4, y0 + 4, x1 - 4, y1, "exam_red")
    dots(d, 100, 19, ["shadow", "step_b", "paper"])
    lay = new_layer()
    ld = ImageDraw.Draw(lay)
    chalkboard(ld, 160, 1, 380, [(10, 3, "S"), (24, 3, "[a,b]"), (56, 3, "A^B"), (84, 3, "{xn}"), (122, 3, "T-1")])
    disc(ld, 440, 7, 5, "paper")  # часы на стене
    rect(ld, 440, 3, 440, 7, "outline")
    rect(ld, 440, 7, 443, 7, "outline")
    x0, y0, x1, y1 = cell(14, 1, 4, 1)  # стол преподавателя: бланки, таймер, печать
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y1 - 1, "wood")
    rect(ld, x0 + 1, y0 + 2, x1 - 1, y0 + 3, "wood_light")
    rect(ld, x0 + 1, y1 - 2, x1 - 1, y1 - 1, "wood_dark")
    rect(ld, x0 + 5, y0 + 4, x0 + 20, y0 + 11, "paper")
    rect(ld, x0 + 24, y0 + 4, x0 + 36, y0 + 11, "paper")
    disc(ld, x0 + 46, y0 + 8, 5, "paper")
    disc(ld, x0 + 46, y0 + 8, 3, "exam_red")
    for i, (cx, cy) in enumerate(H2_DESKS):
        desk(ld, cx, cy)
        bx, by, bx1, by1 = cell(cx, cy, 4, 1)
        exam_sheet(ld, bx + 8, by + 4, "2" if i % 4 == 1 else "F" if i % 4 == 3 else None)
        rect(ld, bx + 24, by + 6, bx + 30, by + 8, "pack")  # карандаш
    x0, y0, x1, y1 = cell(29, 14, 2, 2)  # стопки бланков
    for sx, sy in ((x0 + 2, y0 + 17), (x0 + 2, y0 + 5), (x0 + 16, y0 + 11)):
        rect(ld, sx, sy, sx + 11, sy + 10, "paper")
        rect(ld, sx, sy + 8, sx + 11, sy + 10, "step_b")
        rect(ld, sx + 2, sy + 3, sx + 9, sy + 3, "step_b")
    x0, y0, x1, y1 = cell(1, 16, 3, 1)  # ящик с бланками
    rect(ld, x0 + 1, y0 + 3, x1 - 1, y1 - 2, "box")
    rect(ld, x0 + 1, y0 + 3, x1 - 1, y0 + 5, "wood_light")
    x0, y0, x1, y1 = cell(1, 1, 2, 1)
    rect(ld, x0 + 1, y0 + 1, x1 - 1, y1 - 1, "box")
    rect(ld, x0 + 1, y0 + 1, x1 - 1, y0 + 3, "wood_light")
    rect(ld, x0 + 13, y0 + 1, x0 + 16, y1 - 1, "wood_dark")
    x0, y0, x1, y1 = cell(30, 1)
    rect(ld, x0 + 3, y0 + 8, x1 - 3, y1 - 1, "pot")
    disc(ld, x0 + 7, y0 + 5, 6, "leaf_dark")
    disc(ld, x0 + 6, y0 + 4, 4, "leaf")
    lay_on(img, lay)
    put_door(img, d, 26, "hse_blue_dark")
    return finish(img)


# ---------------------------------------------------------------- пули: слово, нули и единицы, производная
# Пули: 8 готовых положений (0, 45, 90, ... 315 градусов против часовой, 0 = вправо, 90 = вверх), файл 32x32,
# центр пули в центре файла. В игре рисуются 1:1 в (x - 16, y - 16), ничего поворачивать не нужно. 2 кадра мерцания.
FONT.update({
    "s": ["...", ".##", "##.", "..#", "##."], "h": ["#..", "#..", "##.", "#.#", "#.#"],
    "'": ["#", "#", ".", ".", "."],
})
# (уровень, чей): текст или поколение, цвет букв, цвет искр. Герой холодный/жёлтый, боссы красно-оранжевые.
BULLETS = {
    (1, "player"): dict(text="shoot", col="pack", spark="paper"),
    (1, "boss"): dict(text="shoot", col="exam_red", spark="enemy_orange"),
    (2, "player"): dict(text=("1010", "0101"), col="screen", spark="bar_green_light"),
    (2, "boss"): dict(text=("1010", "0101"), col="hit_red", spark="led_amber"),
    (3, "player"): dict(text="f'(x)", col="paper", spark="screen"),
    (3, "boss"): dict(text="f'(x)", col="exam_red", spark="paper"),
}


BULLET_ANGLES = (0, 45, 90, 135, 180, 225, 270, 315)  # 0 вправо, 90 вверх, 180 влево, 270 вниз (против часовой)


def rot_pixels(img, angle):
    """Поворот пиксель-арта: на 45° через 4x-копию и голосование по блокам 4x4, чтобы буквы не рассыпались."""
    if angle % 90 == 0:
        return img.rotate(angle, resample=Image.NEAREST)
    big = img.resize((128, 128), Image.NEAREST).rotate(angle, resample=Image.NEAREST)
    out = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    bp, op = big.load(), out.load()
    for y in range(32):
        for x in range(32):
            cnt = {}
            for yy in range(4):
                for xx in range(4):
                    c = bp[x * 4 + xx, y * 4 + yy]
                    if c[3]:
                        cnt[c] = cnt.get(c, 0) + 1
            if sum(cnt.values()) >= 6:
                op[x, y] = max(cnt, key=cnt.get)
    return out


def bullet(level, who, frame, angle=0):
    """Пуля, повёрнутая на angle градусов против часовой от «вправо». Файл 32x32, центр пули в (16, 16)."""
    cfg = BULLETS[(level, who)]
    body = Image.new("RGBA", (32, 32), (0, 0, 0, 0))  # слово и след, нарисованные горизонтально
    d = ImageDraw.Draw(body)
    txt = cfg["text"][frame - 1] if isinstance(cfg["text"], tuple) else cfg["text"]
    tw = text_width(txt)
    x0, y0 = (32 - tw) // 2 + 1, 8 + 5 - 3 + (frame - 1)  # на втором кадре текст на 1 px ниже
    text(d, x0, y0, txt, cfg["col"])
    for k in range(3):  # след позади (слева) отдельными точками, не слипается с текстом
        d.point((max(1, x0 - 7) + k * 2, y0 + 1 + k % 2 + (frame - 1)), fill=P[cfg["col"]])
    sparks = Image.new("RGBA", (32, 32), (0, 0, 0, 0))  # искры, пыль мела, помехи
    sd = ImageDraw.Draw(sparks)
    seed = frame * 7 + level * 3 + (1 if who == "boss" else 0)
    for i in range(7 if level == 2 else 4):
        sd.point((3 + (seed * (i + 3) * 13 + i * 29) % 26, 8 + 2 + (seed * (i + 5) * 7 + i * 11) % 12), fill=P[cfg["spark"]])
    if level == 2:  # помехи: горизонтальные сбои строк
        gy = 8 + 3 + (frame * 5) % 9
        for x in range(2 + frame * 3, 8 + frame * 3):
            sd.point((x, gy), fill=P[cfg["spark"]])
        for x in range(20 - frame * 2, 26 - frame * 2):
            sd.point((x, 8 + 14 - ((frame * 5) % 9 + 3) // 3), fill=P["paper"] if who == "player" else P["exam_red"])
    if angle:
        body = rot_pixels(body, angle)  # вокруг центра (16, 16), против часовой
        sparks = rot_pixels(sparks, angle)
    outline(body, P["outline"])  # контур 1 px строится после поворота, чтобы остался чистым на диагоналях
    bp, sp = body.load(), sparks.load()
    for y in range(32):
        for x in range(32):
            if bp[x, y][3] == 0 and sp[x, y][3]:
                bp[x, y] = sp[x, y]
    return body


def save_bullets():
    """12 пуль (3 уровня x герой/босс) x 8 направлений x 2 кадра мерцания."""
    for (level, who), _ in BULLETS.items():
        for angle in BULLET_ANGLES:
            for frame in (1, 2):
                save(bullet(level, who, frame, angle), "fx_bullet_l%d_%s_%d_%d" % (level, who, angle, frame))


SIZES = {"bg_": (960, 540), "boss_": (64, 64), "ui_": (320, 44), "fx_bullet_": (32, 32)}  # остальное 32x32


def check():
    """Проверка перед сдачей: ключ = файл, размеры, RGBA, только цвета PALETTE (и тень с альфой 60),
    у персонажей на краях кадра только контур, прозрачность или тень. Возвращает список ошибок."""
    errors = []
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = json.load(f)
    files = {f for f in os.listdir(OUT) if f.endswith(".png")}
    allowed = set(PALETTE.values())
    for key, rel in manifest.items():
        if rel != "images/%s.png" % key or key + ".png" not in files:
            errors.append("%s: нет файла или путь не images/<ключ>.png" % key)
            continue
        img = Image.open(os.path.join(OUT, key + ".png"))
        want = next((v for k, v in SIZES.items() if key.startswith(k)), (32, 32))
        if img.mode != "RGBA" or img.size != want:
            errors.append("%s: %s %s, нужно RGBA %s" % (key, img.mode, img.size, want))
            continue
        colors = {c for _, c in img.getcolors(1 << 20)}
        bad = [c for c in colors if c[3] not in (0, 60, 255) or (c[3] == 255 and c[:3] not in allowed)
               or (c[3] == 60 and c[:3] != (0, 0, 0))]
        if bad:
            errors.append("%s: цвета не из PALETTE: %s" % (key, bad[:3]))
        if key.startswith("bg_") and img.getchannel("A").getextrema()[0] != 255:
            errors.append("%s: фон должен быть непрозрачным" % key)
        if not key.startswith(("bg_", "ui_")):
            w, h = img.size
            px = img.load()
            edge = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
            if any(px[q][3] == 255 and px[q][:3] != P["outline"] for q in edge):
                errors.append("%s: деталь обрезана краем кадра" % key)
    for f in files - {k + ".png" for k in manifest}:
        errors.append("%s: файл без ключа в манифесте" % f)
    return errors


if __name__ == "__main__":
    import sys
    if "--check" in sys.argv:  # только проверка уже нарисованного
        problems = check()
        print("\n".join(problems) or "Проверка: ошибок нет")
        sys.exit(1 if problems else 0)
    # всё в assets/images генерирует этот скрипт: пересобираем с нуля
    if os.path.isdir(OUT):
        for f in os.listdir(OUT):
            if f.endswith(".png"):
                os.remove(os.path.join(OUT, f))
    if os.path.exists(MANIFEST):
        os.remove(MANIFEST)
    save(bg_level3_hall(), "bg_level3_hall")
    save(bg_level3_entrance(), "bg_level3_entrance")
    save_hp_bars()
    save_character("player")
    save_character("boss_level3")
    save_heal_anim()
    save(bg_level1_yard(), "bg_level1_yard")
    save(bg_entrance_l1(), "bg_entrance_l1")
    save(bg_level1_boss(), "bg_level1_boss")
    save(bg_entrance_l2(), "bg_entrance_l2")
    save(bg_level2_class(), "bg_level2_class")
    save(bg_level2_boss(), "bg_level2_boss")
    save(bg_level3_entrance(), "bg_entrance_l3")  # тот же двор Львовки под ключом нового набора
    save(bg_level3_boss(), "bg_level3_boss")
    for npc_key in ("npc_l1_entrance_npc", "npc_l2_entrance_npc", "npc_l3_entrance_npc"):
        save(globals()[npc_key](), npc_key)
    save(fx_heal(), "fx_heal")
    save_bullets()
    save(bg_level1_yard2(), "bg_level1_yard2")
    save(bg_level2_class2(), "bg_level2_class2")
    save(bg_level3_hall2(), "bg_level3_hall2")
    for creature in ("enemy_english_melee", "enemy_binary_melee", "enemy_formula_melee"):
        save_creature(creature)
    save_bird("enemy_hse_bird")
    save_character("boss_level1")
    save_character("boss_level2")
    problems = check()
    print("\n".join(problems) or "Готово: %d ключей, проверка без ошибок" % len(json.load(open(MANIFEST, encoding="utf-8"))))
