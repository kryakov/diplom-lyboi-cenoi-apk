import pygame

from src.ui.text import draw_text, get_font, wrap

BOX = pygame.Rect(60, 380, 840, 130)
PAD = 20
TEXT_SIZE = 22
LINE_H = 28
MAX_LINES = 3

BG = (15, 15, 30)
BORDER = (230, 230, 240)
SPEAKER = (255, 210, 90)
HINT = (160, 160, 170)


def draw_dialogue(surface, session):
    line = getattr(session, "current", None)
    if not line:
        return

    pygame.draw.rect(surface, BG, BOX, border_radius=6)
    pygame.draw.rect(surface, BORDER, BOX, 3, border_radius=6)

    draw_text(surface, line.get("speaker", ""), (BOX.x + PAD, BOX.y + 12), 24, SPEAKER)

    hint = "E / Enter — дальше"
    hint_w = get_font(16).size(hint)[0]
    draw_text(surface, hint, (BOX.right - PAD - hint_w, BOX.y + 16), 16, HINT)

    font = get_font(TEXT_SIZE)
    rows = wrap(line.get("text", ""), font, BOX.w - 2 * PAD)
    if len(rows) > MAX_LINES:
        rows = rows[:MAX_LINES]
        rows[-1] = rows[-1].rstrip(" .,") + "…"
    for i, row in enumerate(rows):
        draw_text(surface, row, (BOX.x + PAD, BOX.y + 44 + i * LINE_H), TEXT_SIZE)