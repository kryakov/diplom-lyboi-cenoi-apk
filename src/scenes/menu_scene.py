import sys
import pygame

from src import settings
from src.core.scene_manager import Scene
#from src.systems import audio
from src.ui.text import draw_text


def difficulty_name():
    table = getattr(settings, "DIFFICULTIES", {})
    return table.get(getattr(settings, "DIFFICULTY", ""), {}).get("name", "")


def change_difficulty(step):
    order = list(getattr(settings, "DIFFICULTY_ORDER", ()))
    if not order:
        return
    current = getattr(settings, "DIFFICULTY", order[0])
    i = order.index(current) if current in order else 0
    settings.DIFFICULTY = order[(i + step) % len(order)]


class MenuScene(Scene):
    ITEMS = ("Играть", "Сложность", "Выход")

    def on_enter(self, **kwargs):
        self.index = 0
        #audio.play_music("menu.ogg")

    def _rect(self, i):
        return pygame.Rect(330, 240 + i * 70, 300, 50)

    def _choose(self, i):
        if i == 0:
            self.game.scenes.change("game")
        elif i == 1:
            change_difficulty(1)
        else:
            self.game.quit()

    def _label(self, i):
        if self.ITEMS[i] == "Сложность" and difficulty_name():
            return f"Сложность: {difficulty_name()}"
        return self.ITEMS[i]

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_w, pygame.K_s):
                step = 1 if event.key == pygame.K_DOWN or event.key == pygame.K_s else -1
                self.index = (self.index + step) % len(self.ITEMS)
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._choose(self.index)
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d) and self.ITEMS[self.index] == "Сложность":
                change_difficulty(1 if event.key in (pygame.K_RIGHT, pygame.K_d) else -1)
            elif event.key == pygame.K_ESCAPE:
                self.game.quit()
            elif event.key == pygame.K_m:
                #audio.toggle_music()
                pass
        elif event.type == pygame.MOUSEMOTION:
            for i in range(len(self.ITEMS)):
                if self._rect(i).collidepoint(event.pos):
                    self.index = i
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i in range(len(self.ITEMS)):
                if self._rect(i).collidepoint(event.pos):
                    self._choose(i)

    def draw(self, surface):
        draw_text(surface, "Диплом любой ценой", (480, 150), 56, center=True)
        for i, name in enumerate(self.ITEMS):
            r = self._rect(i)
            color = (70, 90, 160) if i == self.index else (40, 45, 70)
            pygame.draw.rect(surface, color, r, border_radius=8)
            draw_text(surface, self._label(i), r.center, 28, center=True)
        if self.game.touch.active:
            hint = "Коснитесь пункта: «Сложность» меняется по кругу"
        elif sys.platform == "emscripten":
            hint = "W/S — выбор, A/D — сложность, Enter — подтвердить"   # в браузерном шрифте нет стрелок
        else:
            hint = "↑/↓ — выбор, ←/→ — сложность, Enter — подтвердить, Esc — выход, F11 — окно"
        draw_text(surface, hint, (480, 480), 18, (150, 150, 165), center=True)