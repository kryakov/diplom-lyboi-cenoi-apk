import pygame

from src.core.scene_manager import Scene
from src.ui.dialogue_box import draw_dialogue
from src.ui.text import draw_text

from src import settings

try:
    from src.systems.dialogue import DialogueSession, load_dialogue
except ImportError:
    DialogueSession = load_dialogue = None

RED = (200, 30, 30)
BLUE = (30, 60, 200)
GOLD = (240, 220, 160)
DIPLOMA = pygame.Rect(280, 70, 400, 260)


class EndScene(Scene):
    def on_enter(self, deaths=0, **kwargs):
        self.deaths = deaths
        self.red = deaths <= settings.RED_DIPLOMA_MAX_DEATHS
        self.dialogue = None
        if load_dialogue:
            try:
                self.dialogue = DialogueSession(load_dialogue("ending_red" if self.red else "ending_blue"))
            except Exception:
                self.dialogue = None

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key not in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_e):
            return
        if self.dialogue:
            if self.dialogue.advance():
                self.dialogue = None
        else:
            self.game.scenes.change("menu")

    def draw(self, surface):
        color = RED if self.red else BLUE

        pygame.draw.rect(surface, color, DIPLOMA, border_radius=10)
        pygame.draw.rect(surface, GOLD, DIPLOMA, 4, border_radius=10)
        pygame.draw.rect(surface, GOLD, DIPLOMA.inflate(-24, -24), 1, border_radius=6)

        draw_text(surface, "ДИПЛОМ", (480, 140), 52, GOLD, center=True)
        kind = "с отличием" if self.red else "об окончании"
        draw_text(surface, kind, (480, 190), 24, GOLD, center=True)
        draw_text(surface, f"Смертей: {self.deaths}", (480, 260), 28, center=True)

        if self.dialogue:
            draw_dialogue(surface, self.dialogue)
        else:
            draw_text(surface, "Enter — в меню", (480, 470), 24, (200, 200, 210), center=True)