import pygame


_fonts = {}
def get_font(size):
    if size not in _fonts:
        _fonts[size] = pygame.font.SysFont("arial,segoeui,dejavusans,liberationsans", size)
    return _fonts[size]
def draw_text(surface, text, pos, size=24, color=(255, 255, 255), center=False):
    img = get_font(size).render(text, True, color)
    rect = img.get_rect(center=pos) if center else img.get_rect(topleft=pos)
    surface.blit(img, rect)
def wrap(text, font, max_width):
    lines, line = [], ""
    for word in text.split():
        test = f"{line} {word}".strip()
        if line and font.size(test)[0] > max_width:
            lines.append(line)
            line = word
        else:
            line = test
    return lines + [line] if line else lines